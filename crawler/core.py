import json
import math
import gender_guesser.detector as gender
import bigquery
import os

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

#TO DO: modify to query repo table
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

#TO DO: modify to query repo table
def rank_repo(men, info):
    for person in info:
        fact = info[person]
        score =0
        for l in fact[2]:
            if l['stargazers_count'] !=0:
                score += math.log(l['stargazers_count'])
            if l['open_issues_count'] !=0:
                score -= l['open_issues_count']/(1+l['stargazers_count'])* math.log10(1+l['stargazers_count'])
                score = score/len(fact[2])
        men[person] += score

def find_a_hubby(): 
    d = gender.Detector()
    men = {}
    info = {}
    bq = bigquery.BigQuery()
    client = bq.client
    query_job = client.query("""
    SELECT *
    FROM `precise-tenure-184101.githubby.users` """)
    results = query_job.result() 
    for line in results: 
        name = line['name']
        if type(name) is str: 
            firstname = name.split()[0]
            sex = d.get_gender(firstname)
            if sex != 'female' and sex != 'mostly_female':
                factors = []
                men[line['owner_login']] = 1
                factors.append(line['following'])
                factors.append(line['followers'])
                factors.append(line['repos_url'])
                factors.append(line['created_at'])
                info[line['owner_login']] = factors
    celeb(men,info)
    
    return men
##USED FOR BIG QUERY PARSING IGNORE FOR NOW 
def get_his_repos(men):
    bq = bigquery.BigQuery()
    client = bq.client
    his_repos = {}
    f1 = open('repos.json',"w+")
    for user in men: 
        #print(user)
        query_job = bq.client.query("""
        SELECT *
        FROM `precise-tenure-184101.githubby.repos`
        WHERE owner_login=\'""" + user+ "\'")
        results = query_job.result()
        requirements = []
        for line in results:
            requirements.append(line['commits'])
            requirements.append(line['forks_count'])
            requirements.append(line['open_issues_count'])
        his_repos[user] = requirements
        f1.write(json.dumps({"user":user, "info":his_repos[user]}))
        f1.write('\n')
        #print(his_repos)
      
        #f1.write('\"'+ str(user) + '\":' + str(requirements)+'\n')
    #f1.write(str(his_repos))
    f1.close()
    return his_repos

def them_repos_though(men):
    with open('repos.json') as repos:
        data = json.load(repos)
        print(data)
        for user in data:
            print(data[user])
            dets = data[user]
    print(dets)



hubbies = find_a_hubby()
# f= open("hubbies.txt","w+")
# for user in hubbies:
#     f.write(user + ': ' + str(hubbies[user])+",")
# f.close()
#them_repos_though(hubbies)

#f1 = open('repos.json',"w+")
repos = get_his_repos(hubbies)
#for i in repos:
#    f1.write('\'userid\' :' + i +',\'info\': ' + repos[i])
#f1.close()


# with open('repos.json') as data:
#     for line in data:
#         s = json.loads(line)
#         print(s)
##GOT ALL INFO FROM REPOS, CAN NOW DO OFFLINE ANALYSIS FOR HUBBY SCORE
##GOT DATA NEEDED FOR HUBBIES OTHER FEATURES, CAN NOW COMPUTE OFFLINE SCORE.
##LET'S EFFING GO

        

        