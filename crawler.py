"""Crawler module for collecting GitHub user information."""

from multiprocessing import Pool, Manager
from enum import Enum
import requests

TOKEN = ''
with open('token.txt', 'r') as tokenfile:
    TOKEN = '?access_token=' + tokenfile.readline()
APIURL = 'https://api.github.com/'


class PageType(Enum):
    """Enum for types of content to scrape."""
    USER = 1
    FOLLOWERS = 2


def start():
    """Main function that starts the multithreaded crawler."""

    with Pool(processes=4) as pool:
        manager = Manager()
        jobqueue = manager.Queue()
        jobqueue.put((PageType.USER, 'liamfmoran'))
        jobqueue.put((PageType.USER, 'williamorosky'))
        jobqueue.put((PageType.USER, 'krispekala'))
        res = pool.apply_async(getinfo, (jobqueue,))
        res.get()


def getinfo(jobqueue):
    """Given request, scrape GitHub."""
    while not jobqueue.empty():
        req = jobqueue.get(True)

        pagetype = req[0]
        item = req[1]

        res = {
            PageType.USER: jobuser,
            PageType.FOLLOWERS: jobfollowers
        }[pagetype](jobqueue, item)

        print(item, 'collected')


def jobfollowers(jobqueue, username):
    """Adds more jobs to jobqueue from followers list."""
    followers = getfollowers(username)
    for user in followers:
        jobqueue.put((PageType.USER, user))


def getfollowers(username):
    """Creates list of followers."""
    reqjson = requests.get(APIURL + 'users/' + username +
                           '/followers' + TOKEN).json()

    if 'message' in reqjson:
        print(username, 'not found')
        print(reqjson)
        return {}

    retval = []
    for follower in reqjson:
        retval.append(follower['login'])

    return retval


def jobuser(jobqueue, username):
    """Adds more jobs to jobqueue and fetches user info."""
    jobqueue.put((PageType.FOLLOWERS, username))
    return getuser(username)


def getuser(username):
    """Creates dictionary of necessary user information."""
    reqjson = requests.get(APIURL + 'users/' + username + TOKEN).json()

    if 'message' in reqjson:
        print(username, 'not found')
        print(reqjson)
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


if __name__ == "__main__":
    start()
