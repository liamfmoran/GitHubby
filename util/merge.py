import json

with open('users.dat', 'r') as userfile, open('repos.dat', 'r') as reposfile, open('usersrepos.dat', 'w') as userrepofile:
    for line in userfile.readlines():
        user = json.loads(line)
        user['repos'] = []
        for repoline in reposfile.readlines():
            repo = json.loads(repoline)
            if repo['owner_id'] == user['id']:
                user['repos'].append(repo)
        json.dump(user, userrepofile)
        userrepofile.write('\n')
        reposfile.seek(0)
