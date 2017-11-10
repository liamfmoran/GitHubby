"""Crawler module for collecting GitHub user information."""

from multiprocessing import Lock, Manager, Pool
from enum import Enum
import json
import sys
# import os
import time
import requests


TOKENINDEX = 0
with open('token.txt', 'r') as tokenfile:
    TOKENS = [line.rstrip() for line in tokenfile.readlines()]
APIURL = 'https://api.github.com/'

LOCK = Lock()


class PageType(Enum):
    """Enum for types of content to scrape."""
    USER = 1
    FOLLOWERS = 2
    FOLLOWING = 3
    REPOS = 4
    CONTRIBUTORS = 5
    STARGAZERS = 6


def start():
    """Main function that starts the multithreaded crawler."""
    visited = set()

    # if os.path.isfile('users.dat') and False:
    #     with open('users.dat') as userfile:
    #         for line in userfile.readlines():
    #             visited.add(line.strip())

    with Pool(processes=4) as userpool, Pool(processes=4) as jobpool:
        manager = Manager()
        lock = manager.Lock()
        userqueue = manager.Queue()
        jobqueue = manager.Queue()

        userqueue.put('liamfmoran')
        userqueue.put('williamorosky')
        userqueue.put('krispekala')

        userres = userpool.apply_async(
            getuserinfo, (userqueue, jobqueue, visited, lock))
        jobres = jobpool.apply_async(
            getjobinfo, (userqueue, jobqueue, visited, lock))

        userres.get()
        jobres.get()


def getuserinfo(userqueue, jobqueue, visited, lock):
    """Given job from user queue, scrape GitHub."""
    with open('users.dat', 'w') as userfile:
        while True:
            # Busy wait to pause the crawler
            # while 'CRAWL' not in os.environ or os.getenv() is False:
            #     time.sleep(1)

            username = userqueue.get(True)

            completed = jobuser(jobqueue, username, visited)

            if completed:
                with lock:
                    json.dump(completed, userfile)
                    userfile.write('\n')
                    userfile.flush()


def getjobinfo(userqueue, jobqueue, visited, _):
    """Given job from job queue, scrape GitHub."""
    while True:
        # Busy wait to pause the crawler
        # while 'CRAWL' not in os.environ or os.environ['CRAWL'] is False:
        #     time.sleep(1)

        req = jobqueue.get(True)

        pagetype = req[0]
        item = req[1]

        # Determine job type and call appropriate function
        pair = {
            PageType.FOLLOWERS: (jobfollowers, userqueue),
            PageType.FOLLOWING: (jobfollowing, userqueue),
            PageType.REPOS: (jobrepos, jobqueue),
            PageType.CONTRIBUTORS: (jobcontributors, userqueue),
            PageType.STARGAZERS: (jobstargazers, userqueue)
        }[pagetype]

        jobfunc = pair[0]
        queue = pair[1]

        jobfunc(queue, item, visited)


# USER JOB


def jobuser(jobqueue, username, visited):
    """Adds more jobs to jobqueue and fetches user info."""
    if (PageType.USER, username) in visited:
        return False
    userinfo = getuser(username)
    # If there are followers, add a job to get them
    if userinfo['followers'] > 0:
        jobqueue.put((PageType.FOLLOWERS, username))
    # If there are following, add a job to get them
    if userinfo['following'] > 0:
        jobqueue.put((PageType.FOLLOWING, username))
    # If there are repos, add a job to get them
    if userinfo['public_repos'] > 0:
        jobqueue.put((PageType.REPOS, username))
    visited.add((PageType.USER, username))
    # print(str(len(visited)) + ':', username, 'collected')
    return userinfo


def getuser(username):
    """Creates dictionary of necessary user information."""
    request = APIURL + 'users/' + username
    reqjson = gettoken(request)

    return parseuser(reqjson)


def parseuser(userjson):
    """Parses user JSON for desired information."""
    retval = {}
    retval['login'] = userjson['login']
    retval['id'] = userjson['id']
    retval['avatar_url'] = userjson['avatar_url']
    retval['followers_url'] = userjson['followers_url']
    # Trim off '{/other_user}'
    retval['following_url'] = userjson['following_url'][:-13]
    # Trim off '{/owner}{/repo}'
    retval['starred_url'] = userjson['starred_url'][:-15]
    retval['subscriptions_url'] = userjson['subscriptions_url']
    retval['repos_url'] = userjson['repos_url']
    retval['events_url'] = userjson['events_url']
    retval['name'] = userjson['name']
    retval['company'] = userjson['company']
    retval['blog'] = userjson['blog']
    retval['location'] = userjson['location']
    retval['bio'] = userjson['bio']
    retval['public_repos'] = userjson['public_repos']
    retval['followers'] = userjson['followers']
    retval['following'] = userjson['following']
    retval['created_at'] = userjson['created_at']
    retval['updated_at'] = userjson['updated_at']

    return retval


# FOLLOWER JOB


def jobfollowers(userqueue, username, visited):
    """Adds more jobs to jobqueue from followers list."""
    sys.stdout.flush()
    followers = getfollowers(username)
    for user in followers:
        if (PageType.USER, user) not in visited:
            userqueue.put(user)


def getfollowers(username):
    """Creates list of followers."""
    request = APIURL + 'users/' + username + '/followers'
    reqjson = gettoken(request)

    retval = []
    for follower in reqjson:
        retval.append(follower['login'])

    return retval


# FOLLOWING JOB


def jobfollowing(userqueue, username, visited):
    """Adds more jobs to jobqueue from following list."""
    following = getfollowing(username)
    for user in following:
        if (PageType.USER, user) not in visited:
            userqueue.put(user)


# Consider just making this a generic getuserlist method
def getfollowing(username):
    """Creates list of leaders."""
    request = APIURL + 'users/' + username + '/following'
    reqjson = gettoken(request)

    retval = []
    for leader in reqjson:
        retval.append(leader['login'])

    return retval


# REPO JOB


def jobrepos(jobqueue, username, visited):
    """Adds more jobs to the jobqueue from a user's repos list."""
    repos = getrepos(username)
    for repo in repos:
        if (PageType.REPOS, (username, repo['name'])) not in visited:
            # If the repo is empty, skip it
            if repo['size'] == 0:
                continue
            # Begin putting all the info I want to get off of a repo here
            jobqueue.put((PageType.CONTRIBUTORS, [username, repo['name']]))
            # If there are stargazers, add a job to get them
            if repo['stargazers_count'] > 0:
                jobqueue.put((PageType.STARGAZERS, [username, repo['name']]))


def getrepos(username):
    """Creates a list of repos."""
    request = APIURL + 'users/' + username + '/repos'
    reqjson = requests.get(request).json()

    retval = []
    for repo in reqjson:
        parsedrepo = parserepo(repo)
        retval.append(parsedrepo)

    return retval


def parserepo(repojson):
    """Parses repo JSON for desired information."""
    retval = repojson

    retval['id'] = repojson['id']
    retval['name'] = repojson['name']
    retval['full_name'] = repojson['full_name']
    retval['size'] = repojson['size']
    retval['stargazers_count'] = repojson['stargazers_count']

    return retval


# CONTRIBUTOR JOB


def jobcontributors(userqueue, params, visited):
    """Adds more jobs to the jobqueue from repo's contributor list."""
    contributors = getcontributors(params[0], params[1])
    for contributor in contributors:
        # TODO: Remove this maybe because now we ignore type
        if (PageType.USER, contributor) not in visited:
            userqueue.put(contributor)


def getcontributors(username, repo):
    """Creates a list of users."""
    request = APIURL + 'repos/' + username + '/' + repo + '/contributors'
    reqjson = gettoken(request)

    retval = []
    for user in reqjson:
        retval.append(user['login'])

    return retval


# STARGAZER JOB


def jobstargazers(userqueue, params, visited):
    """Adds more jobs to the jobqueue from repo's contributor list."""
    stargazers = getstargazers(params[0], params[1])
    for stargazer in stargazers:
        if (PageType.USER, stargazer) not in visited:
            userqueue.put(stargazer)


def getstargazers(username, repo):
    """Creates a list of users."""
    request = APIURL + 'repos/' + username + '/' + repo + '/stargazers'
    reqjson = gettoken(request)

    retval = []
    for user in reqjson:
        retval.append(user['login'])

    return retval


# HELPER FUNCTION


def getuserlist(url):
    """Creates a list of users."""
    reqjson = requests.get(url).json()

    retval = []
    for user in reqjson:
        retval.append(user['login'])
    return retval


def gettoken(url):
    """Gets token and switches token if max tries occurs."""
    global TOKENINDEX

    while True:
        try:
            request = url + '?access_token=' + TOKENS[TOKENINDEX]
            reqjson = requests.get(request).json()
            if 'message' in reqjson:
                print('ERROR:', reqjson['message'])
                raise ConnectionError
            return reqjson
        except ConnectionError:
            with LOCK:
                TOKENINDEX = (TOKENINDEX + 1) % len(TOKENS)
            time.sleep(1)


# COLLABORATOR JOB - This does not work becuase push access is required with authentication


if __name__ == "__main__":
    start()
