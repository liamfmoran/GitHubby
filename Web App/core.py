import json
import math
import sexmachine.detector as gender
import bigquery
import os


##Popularity
def celeb(men, info):
    for person in info:
        fact = info[person]
        if fact[0]<= fact[1]:
            men[person] +=1

#TO DO: modify to query repo table
def languages(men, info, importance):
    for person in men:
        if person not in info:
            continue
        his_langs = {}
        for i in info[person]:
            if i not in his_langs:
                his_langs[i] = 0
            his_langs[i] +=1
        sum1 = 0
        for l in his_langs:
            sum1 += his_langs[l]
        mean = float(sum1)/len(his_langs)
        tots = 0
        for l in his_langs:
            tots += (his_langs[l]-mean)**2
        var = float(tots)+1/len(his_langs)
        men[person] += (importance*0.1) * float(1)/var
          
        
    #eturn user_and_languages

#TO DO: modify to query repo table
def rank_repo(men, info,does_size_matter,do_you_want_kids,import_loyalty, privacy):
    stff = {}
    dum = 0
    loyalty = {}
    for person in info:
        his_langs = []
        score =0
        stff[person] = 0
        if len(info[person]) == 0:
            continue
        while len(info[person]) != 0:
            num_repos = 0
            test = json.loads(info[person][0])
            for l in test:
                ## DOES SIZE MATTER
                size = l['stats']['total']
                stff[person] += size
                num_repos += 1
                dum += size
                repo_length = l['length']
            ##DO YOU WANT KIDS/ HOW MANY KIDS
            fork_count = info[person][1]
            if do_you_want_kids == 'yes':
                men[person] += math.log10(fork_count+1)

            open_issues = info[person][2]
            stargazers_count = info[person][3]
            his_langs.append(info[person][4])

            if stargazers_count !=0:
                 score += math.log(stargazers_count)
            if open_issues !=0:
                score -= float(open_issues)/(1+stargazers_count)* math.log10(1+stargazers_count)
                score = float(score)/(repo_length+1)
            info[person] = info[person][5:]
        men[person] += score
        ##HOW IMPORTABT IS PRIVACY == NUM OF HIS REPOS
        stff[person] = float(stff[person])/num_repos

        ##HOW IMPORTANT IS LOYALTY == LANGUAGE VARIANCE
        loyalty[person] = his_langs
    ## DOES SIZE MATTER?! 
    if does_size_matter == 'yes':
        mean = dum/len(stff)
        for guy in stff:
            if stff[guy] < mean :
                men[guy] -= 1
            if stff[guy] > mean :
                men[guy] +=1 
    ## HOW IMPORTANT IS LOYALTY
        languages(men, loyalty, import_loyalty)
    print(men)


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
            requirements.append(line['stargazers_count'])
            requirements.append(line['langauge'])
        his_repos[user] = requirements
        f1.write(json.dumps({"user":user, "info":his_repos[user]}))
        f1.write('\n')
        #print(his_repos)
      
        #f1.write('\"'+ str(user) + '\":' + str(requirements)+'\n')
    #f1.write(str(his_repos))
    f1.close()
    return his_repos

def them_repos_though(men,does_size_matter,do_you_want_kids,import_loyalty, privacy):
  with open('repos.json') as data:
    repos = {}
    for line in data:
        s = json.loads(line)
        repos[s['user']] = s['info']

    rank_repo(men, repos,does_size_matter,do_you_want_kids,import_loyalty, privacy) 
    #print(dets)




#repos = get_his_repos(hubbies)

# with open('repos.json') as data:
#     repos = {}
#     for line in data:
#         s = json.loads(line)
#         repos[s['user']] = s['info']
#     print(repos) 
##GOT ALL INFO FROM REPOS, CAN NOW DO OFFLINE ANALYSIS FOR HUBBY SCORE
##GOT DATA NEEDED FOR HUBBIES OTHER FEATURES, CAN NOW COMPUTE OFFLINE SCORE.
##LET'S EFFING GO

        

        