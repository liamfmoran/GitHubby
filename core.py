import json
import math
import gender_guesser.detector as gender

def celeb(men, info):
    for person in info:
        fact = info[person]
        if fact[0]<= fact[1]:
            men[person] +=1
   
def lots_of_repos(men,info):
    for person in info:
        fact = info[person]
        if len(fact[2]) != 0:
            men[person] += math.log10(len(fact[2]))

def languages(info):
    user_and_languages = {}
    for person in info:
        langs = []
        fact = info[person]
        for l in fact[2]:
            if l['language'] not in langs:
                langs.append(l['language'])
        user_and_languages[person] = langs
    return user_and_languages


def rank_repo(men, info):
    for person in info:
        fact = info[person]
        score =0
        for l in fact[2]:
            if l['stargazers_count'] !=0:
              score += math.log(l['stargazers_count'])
              if l['open_issues_count'] !=0:
                  score += (l['open_issues_count']/l['stargazers_count'])*math.log(l['stargazers_count'])
                  



with open('userrepo.dat') as data:
    d = gender.Detector()
    men = {}
    info = {}
    for line in data: 
        users = json.loads(line)
        name = users['name']
        if type(name) is str: 
            firstname = name.split()[0]
            sex = d.get_gender(firstname)
            if sex != 'female' and sex != 'mostly_female':
                factors = []
                men[name] = 1
                factors.append(users['following'])
                factors.append(users['followers'])
                factors.append(users['repos'])
                info[name] = factors

    celeb(men, info)
    lots_of_repos(men,info)
    what = languages(info)
    rank_repo(men, info)
    #print(what)
#print(men)
        

        