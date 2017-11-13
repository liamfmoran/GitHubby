import json

with open('users.dat') as data:
    for line in data: 
        users = json.loads(line)
        print(users['login'])
        