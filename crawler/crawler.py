"""Crawler module for collecting GitHub user information."""

from enum import Enum
import json
from queue import Queue
import sys
import time
import bigquery
import requests


TOKENINDEX = 0
with open('./token.txt', 'r') as tokenfile:
    TOKENS = [line.rstrip() for line in tokenfile.readlines()]
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

    bq = bigquery.BigQuery()

    queue = Queue()

    queue.put((PageType.USER, 'liamfmoran'))
    queue.put((PageType.USER, 'williamorosky'))
    queue.put((PageType.USER, 'krispekala'))

    getinfo(queue, visited, bq)


def getinfo(queue, visited, bq):
    """Given job from job queue, scrape GitHub."""

    while True:
        req = queue.get()

        pagetype = req[0]
        item = req[1]

        # Determine job type and call appropriate function
        pair = {
            PageType.USER: (jobuser, queue),
            PageType.FOLLOWERS: (jobfollowers, queue),
            PageType.FOLLOWING: (jobfollowing, queue),
            PageType.REPOS: (jobrepos, queue),
            PageType.CONTRIBUTORS: (jobcontributors, queue),
            PageType.STARGAZERS: (jobstargazers, queue)
        }[pagetype]

        jobfunc = pair[0]
        queue = pair[1]

        completed = jobfunc(queue, item, visited)

        if pagetype == PageType.REPOS and completed:
            rows = []
            for repo in completed:
                row = maptobq(repo, PageType.REPOS)
                rows.append(row)
            bq.insertrepo(rows)

        if pagetype == PageType.USER and completed:
            row = [ maptobq(completed, PageType.USER) ]
            bq.insertuser(row)


# USER JOB


def jobuser(queue, username, visited):
    """Adds more jobs to queue and fetches user info."""
    if (PageType.USER, username) in visited:
        return None
    userinfo = getuser(username)
    # If there are followers, add a job to get them
    if userinfo['followers'] > 0:
        queue.put((PageType.FOLLOWERS, username))
    # If there are following, add a job to get them
    if userinfo['following'] > 0:
        queue.put((PageType.FOLLOWING, username))
    # If there are repos, add a job to get them
    if userinfo['public_repos'] > 0:
        queue.put((PageType.REPOS, username))
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
    # Trim off '{/privacy}'
    retval['events_url'] = userjson['events_url'][:-10]
    retval['name'] = userjson['name']
    retval['company'] = userjson['company']
    retval['blog'] = userjson['blog']
    retval['location'] = userjson['location']
    retval['bio'] = None if userjson['bio'] == '' else userjson['bio']
    retval['public_repos'] = userjson['public_repos']
    retval['followers'] = userjson['followers']
    retval['following'] = userjson['following']
    retval['created_at'] = userjson['created_at']
    retval['updated_at'] = userjson['updated_at']

    return retval


# FOLLOWER JOB


def jobfollowers(queue, username, visited):
    """Adds more jobs to queue from followers list."""
    sys.stdout.flush()
    followers = getfollowers(username)
    for user in followers:
        if (PageType.USER, user) not in visited:
            queue.put((PageType.USER, user))


def getfollowers(username):
    """Creates list of followers."""
    request = APIURL + 'users/' + username + '/followers'
    reqjson = gettoken(request)

    retval = []
    for follower in reqjson:
        retval.append(follower['login'])

    return retval


# FOLLOWING JOB


def jobfollowing(queue, username, visited):
    """Adds more jobs to queue from following list."""
    following = getfollowing(username)
    for user in following:
        if (PageType.USER, user) not in visited:
            queue.put((PageType.USER, user))


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


def jobrepos(queue, username, visited):
    """Adds more jobs to the queue from a user's repos list."""
    repos = getrepos(username)
    for repo in repos:
        if (PageType.REPOS, (username, repo['name'])) not in visited:
            # Begin putting all the info I want to get off of a repo here
            queue.put((PageType.CONTRIBUTORS, [username, repo['name']]))
            # If there are stargazers, add a job to get them
            if repo['stargazers_count'] > 0:
                queue.put((PageType.STARGAZERS, [username, repo['name']]))

    return repos


def getrepos(username):
    """Creates a list of repos."""
    request = APIURL + 'users/' + username + '/repos'
    reqjson = gettoken(request)

    retval = []
    for repo in reqjson:
        # If the repo is empty, skip it
        if repo['size'] == 0:
            continue
        parsedrepo = parserepo(repo)
        request = parsedrepo['commits_url']
        reqjson = gettoken(request)
        # TODO: Convert JSON to String
        parsedrepo['commits'] = json.dumps(parsecommits(reqjson))
        retval.append(parsedrepo)

    return retval


def parserepo(repojson):
    """Parses repo JSON for desired information."""
    retval = {}

    retval['id'] = repojson['id']
    retval['name'] = repojson['name']
    retval['full_name'] = repojson['full_name']
    retval['owner_login'] = repojson['owner']['login']
    retval['owner_id'] = repojson['owner']['id']
    retval['description'] = repojson['description']
    retval['forks_url'] = repojson['forks_url']
    retval['events_url'] = repojson['events_url']
    retval['languages_url'] = repojson['languages_url']
    # Trim off '{/sha}'
    retval['commits_url'] = repojson['commits_url'][:-6]
    retval['created_at'] = repojson['created_at']
    retval['updated_at'] = repojson['updated_at']
    retval['pushed_at'] = repojson['pushed_at']
    retval['size'] = repojson['size']
    retval['stargazers_count'] = repojson['stargazers_count']
    retval['language'] = repojson['language']
    retval['has_wiki'] = repojson['has_wiki']
    retval['forks_count'] = repojson['forks_count']
    retval['open_issues_count'] = repojson['open_issues_count']

    return retval


def parsecommits(commitsjson):
    """Parses commits JSON for desired information."""
    commitlist = []

    for commit in commitsjson:
        commitval = {}
        if commit['author'] != None:
            commitval['date'] = commit['commit']['author']['date']
            # FIXME: Key error with 'id' because user author does not contain ID
            commitval['user_id'] = commit['author']['id']

        request = commit['url']
        reqjson = gettoken(request)

        (commitval['length'], commitval['stats']) = parsecommit(reqjson) 

        commitlist.append(commitval)

    return commitlist


def parsecommit(commitjson):
    """Parses tree JSON for desired information."""
    retval = (len(commitjson['files']), commitjson['stats'])
    return retval


# CONTRIBUTOR JOB


def jobcontributors(queue, params, visited):
    """Adds more jobs to the queue from repo's contributor list."""
    contributors = getcontributors(params[0], params[1])
    for contributor in contributors:
        # TODO: Remove this maybe because now we ignore type
        if (PageType.USER, contributor) not in visited:
            queue.put((PageType.USER, contributor))


def getcontributors(username, repo):
    """Creates a list of users."""
    request = APIURL + 'repos/' + username + '/' + repo + '/contributors'
    reqjson = gettoken(request)

    retval = []
    for user in reqjson:
        retval.append(user['login'])

    return retval


# STARGAZER JOB


def jobstargazers(queue, params, visited):
    """Adds more jobs to the queue from repo's contributor list."""
    stargazers = getstargazers(params[0], params[1])
    for stargazer in stargazers:
        if (PageType.USER, stargazer) not in visited:
            queue.put((PageType.USER, stargazer))


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
            # We must check if committer is not in reqjson, because the commit JSON contains a message
            if 'message' in reqjson and 'committer' not in reqjson:
                print('ERROR:', reqjson['message'])
                raise ConnectionError
            return reqjson
        except ConnectionError:
            print('CONNECTION ERROR: Switching tokens')
            TOKENINDEX = (TOKENINDEX + 1) % len(TOKENS)
            time.sleep(30)
        else:
            print('UKNOWN ERROR')
            time.sleep(30)


# UTIL

USERCOLS = ['id', 'login', 'avatar_url', 'followers_url', 'following_url', 'starred_url', 'subscriptions_url', 'repos_url', 'events_url', 'name', 'company', 'blog', 'location', 'bio', 'public_repos', 'followers', 'following', 'created_at', 'updated_at']
REPOCOLS = ['id', 'name', 'full_name', 'owner_login', 'owner_id', 'description', 'forks_url', 'events_url', 'languages_url', 'commits_url', 'commits', 'created_at', 'updated_at', 'pushed_at', 'size', 'stargazers_count', 'language', 'has_wiki', 'forks_count', 'open_issues_count']

def maptobq(itemmap, itemtype):
    """Takes a map and converts it to a tuple for BigQuery."""
    retval = None

    if itemtype == PageType.USER:
        retval = [ itemmap[col] for col in USERCOLS ]
    else:
        retval = [ itemmap[col] for col in REPOCOLS ]

    return tuple(retval)




if __name__ == "__main__":
    start()
