"""Crawler module for collecting GitHub user information."""

from multiprocessing import Lock, Manager, Pool 
from enum import Enum
import json
import os
import time
import requests

TOKEN = ''
with open('token.txt', 'r') as tokenfile:
    TOKEN = '?access_token=' + tokenfile.readline()
APIURL = 'https://api.github.com/'


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

    with Pool(processes=4) as pool:
        manager = Manager()
        lock = manager.Lock()
        userqueue = manager.Queue()
        userqueue.put((PageType.USER, 'liamfmoran'))
        userqueue.put((PageType.USER, 'williamorosky'))
        userqueue.put((PageType.USER, 'krispekala'))
        res = pool.apply_async(getinfo, (userqueue, visited, lock))
        res.get()


def getinfo(jobqueue, visited, lock):
    """Given request, scrape GitHub."""
    with open('usersadfsds.dat', 'w', 0) as userfile:
        while not jobqueue.empty():
            # Busy wait to pause the crawler
            # while 'CRAWL' not in os.environ or os.environ['CRAWL'] is False:
            #     time.sleep(1)

            req = jobqueue.get(True)

            pagetype = req[0]
            item = req[1]

            # Determine job type and call appropriate function
            completed = {
                PageType.USER: jobuser,
                PageType.FOLLOWERS: jobfollowers,
                PageType.FOLLOWING: jobfollowing,
                PageType.REPOS: jobrepos,
                PageType.CONTRIBUTORS: jobcontributors,
                PageType.STARGAZERS: jobstargazers
            }[pagetype](jobqueue, item, visited)

            if pagetype == PageType.USER and completed is not False:
                with lock:
                    # json.dump(completed, userfile)
                    pass
                    
            userfile.write('hello\n',)

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
    request = APIURL + 'users/' + username + TOKEN
    reqjson = requests.get(request).json()

    if 'message' in reqjson:
        print('ERROR:', reqjson['message'])
        return {}

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
    # Trim off '{/gist_id}'
    retval['gists_url'] = userjson['gists_url'][:-10]
    # Trim off '{/owner}{/repo}'
    retval['starred_url'] = userjson['starred_url'][:-15]
    retval['subscriptions_url'] = userjson['subscriptions_url']
    retval['organizations_url'] = userjson['organizations_url']
    retval['repos_url'] = userjson['repos_url']
    retval['name'] = userjson['name']
    retval['company'] = userjson['company']
    retval['blog'] = userjson['blog']
    retval['location'] = userjson['location']
    retval['bio'] = userjson['bio']
    retval['public_repos'] = userjson['public_repos']
    retval['public_gists'] = userjson['public_gists']
    retval['followers'] = userjson['followers']
    retval['following'] = userjson['following']
    retval['created_at'] = userjson['created_at']

    #TODO: Create a way to grab the GitHub graph from a user

    return retval


# FOLLOWER JOB


def jobfollowers(jobqueue, username, visited):
    """Adds more jobs to jobqueue from followers list."""
    followers = getfollowers(username)
    for user in followers:
        if (PageType.USER, user) not in visited:
            jobqueue.put((PageType.USER, user))
    return True


def getfollowers(username):
    """Creates list of followers."""
    request = APIURL + 'users/' + username + '/followers' + TOKEN
    reqjson = requests.get(request).json()

    if 'message' in reqjson:
        print('ERROR:', reqjson['message'])
        return {}

    retval = []
    for follower in reqjson:
        retval.append(follower['login'])

    return retval


# FOLLOWING JOB


def jobfollowing(jobqueue, username, visited):
    """Adds more jobs to jobqueue from following list."""
    following = getfollowing(username)
    for user in following:
        if (PageType.USER, user) not in visited:
            jobqueue.put((PageType.USER, user))
    return True


# Consider just making this a generic getuserlist method
def getfollowing(username):
    """Creates list of leaders."""
    request = APIURL + 'users/' + username + '/following' + TOKEN
    reqjson = requests.get(request).json()

    if 'message' in reqjson:
        print('ERROR:', reqjson['message'])
        return []

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
    return True


def getrepos(username):
    """Creates a list of repos."""
    request = APIURL + 'users/' + username + '/repos' + TOKEN
    reqjson = requests.get(request).json()

    if 'message' in reqjson:
        print('ERROR:', reqjson['message'])
        return []

    retval = []
    for repo in reqjson:
        parsedrepo = parserepo(repo)
        retval.append(parsedrepo)

    return retval


def parserepo(repojson):
    """Parses repo JSON for desired information."""
    retval = repojson

    # TODO: Add info we need for repo here
    retval['name'] = repojson['name']
    retval['full_name'] = repojson['full_name']
    retval['size'] = repojson['size']
    retval['stargazers_count'] = repojson['stargazers_count']

    return retval


# CONTRIBUTOR JOB


def jobcontributors(jobqueue, params, visited):
    """Adds more jobs to the jobqueue from repo's contributor list."""
    contributors = getcontributors(params[0], params[1])
    for contributor in contributors:
        if (PageType.USER, contributor) not in visited:
            jobqueue.put((PageType.USER, contributor))
    return True


def getcontributors(username, repo):
    """Creates a list of users."""
    request = APIURL + 'repos/' + username + '/' + repo + '/contributors' + TOKEN
    reqjson = requests.get(request).json()

    if 'message' in reqjson:
        print('ERROR:', reqjson['message'])
        return []

    retval = []
    for user in reqjson:
        retval.append(user['login'])

    return retval


# STARGAZER JOB


def jobstargazers(jobqueue, params, visited):
    """Adds more jobs to the jobqueue from repo's contributor list."""
    stargazers = getstargazers(params[0], params[1])
    for stargazer in stargazers:
        if (PageType.USER, stargazer) not in visited:
            jobqueue.put((PageType.USER, stargazer))
    return True


def getstargazers(username, repo):
    """Creates a list of users."""
    request = APIURL + 'repos/' + username + '/' + repo + '/stargazers' + TOKEN
    reqjson = requests.get(request).json()

    if 'message' in reqjson:
        print('ERROR:', reqjson['message'])
        return []

    retval = []
    for user in reqjson:
        retval.append(user['login'])

    return retval


# HELPER FUNCTION


def getuserlist(url):
    """Creates a list of users."""
    reqjson = requests.get(url).json()

    if 'message' in reqjson:
        print('ERROR:', reqjson['message'])
        return []

    retval = []
    for user in reqjson:
        retval.append(user['login'])
    return retval


# COLLABORATOR JOB - This does not work becuase push access is required with authentication


if __name__ == "__main__":
    start()
