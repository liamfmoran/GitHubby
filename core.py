import json
import math
import gender_guesser.detector as gender
import sys
import os

sys.path.insert(0, './crawler/')

import bigquery


# TODO: Implement these metrics for score
# PREFERENCE - Male/Female
#     - This just filters based on girl/guy preference
# AGE - 18-85
#     - This uses age of account, this might be usless?
# SIZE - Yes/No
#     - Consider the size of the repo
# LOYALTY - 1-5
#     - Variance in languge use
# ATTENTION - 1-5
#     - Number of commits (how much attention they can give you)
# MONEY - 1-5
#     - Average pay for langauge
# KIDS - Yes/No
#     - Number of forks (higher possibility of getting prego)
# PRIVACY - 1-5
#     - Public vs private repos

# NOTE: Maybe we should use this to hold information from a user?
class Score:
    """Scores across features for individual users."""

    def __init__(self, userrow):

        # Gender preference
        self.ismale = False

        # Size
        self.scoresize = 0
        self.weightsize = 1

        # Loyalty
        self.scoreloyalty = 0
        self.weightloyalty = 1

        # Attention
        self.scoreattention = 0
        self.weightattention = 1

        # Money
        self.scoremoney = 0
        self.weightmoney = 1

        # Kids
        self.scorekids = 0
        self.weightkids = 1

        # Privacy
        self.scoreprivacy = 0
        self.weightprivacy = 1


    def getsize(self):
        # Consider number of commits
        # TODO: Finish this shit here
        pass


    def getloyalty(self):
        # Consider variance of languages
        pass


bq = bigquery.BigQuery()

maleusers = {}
femaleusers = {}

def query(preference, age, size, loyalty, attention, money, kids, privacy):
    """Search for users in database."""
    global maleusers, femaleusers
    
    # Get data if not cached
    if maleusers == [] or femaleusers == []:
        gd = gender.Detector()
        maleusers, femaleusers = bq.queryall()

    # Query by preference
    users = None
    if preference == 'Male':
        if len(maleusers) == 0:
            client = bq.client
            # TODO: Query to get male users
            pass
        users = maleusers
    # Otherwise, if preference is female
    else:
        if len(femaleusers) == 0:
            # TODO: Query to get female users
            pass
        users = femaleusers

    # Now we have the users, so let's get distances


##Popularity
def celeb(men, info):
    for person in info:
        fact = info[person]
        if fact[0] <= fact[1]:
            men[person] += 1


def logistic(x, maxnnum):
    """Normalizes a value to be between 1 and maxnum."""
    val = maxnum / (1 + math.exp(-x))
    return int(val+1)



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
        var = logistic(var)
        men[person] += var
          
        
    #eturn user_and_language

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
                ## DOES SIZE MATTER 'YES' OR 'NO' (NO WILL BE A 1 AND YES WILL BE A 5)
                size = l['stats']['total']
                stff[person] += size
                num_repos += 1
                dum += size
                repo_length = l['length']
            ##DO YOU WANT KIDS 'YES' OR 'NO' (NO WILL BE A 1 AND YES WILL BE A 5)
            fork_count = info[person][1]

            #open_issues = info[person][2]
            #stargazers_count = info[person][3]
            his_langs.append(info[person][4])

        #     if stargazers_count !=0:
        #          score += math.log(stargazers_count)
        #     if open_issues !=0:
        #         score -= float(open_issues)/(1+stargazers_count)* math.log10(1+stargazers_count)
        #         score = float(score)/(repo_length+1)
        #     info[person] = info[person][5:]
        # men[person] += score
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
    res = dict((v, k) for k, v in men.items())
    sort = sorted(res, reverse=True)[:10]
    retval = [ { "id": res[guyd] for guyd in sort } ]
    return [ res[x] for x in sorted(res, reverse=True)[:10] ]



def find_a_hubby():
    """Queries BigQuery and gets data from men and initalizes score."""
    # TODO: I think BigQuery.queryall can just be called now wihch will sort by gender
    # NOTE: The above should only be done if the local dictionaries are empty
    
    bq = bigquery.BigQuery()
    male, female = bq.queryall()

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
                factors.append(line['id'])
                factors.append(line['name'])
                factors.append(line['location'])
                info[line['owner_login']] = factors
    celeb(men,info)
    
    return men, info
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
    f1.close()
    return his_repos

def them_repos_though(men,info,does_size_matter,do_you_want_kids,import_loyalty, privacy):
  with open('repos.json') as data:
    repos = {}
    mans = {}
    for line in data:
        s = json.loads(line)
        mans[s['user']] = { 'id': info[s['user']][4], 'name': info[s['user']][5], 'username': s['user'], 'location': info[s['user']][6], 'email': 'godcoder@google.com'}
        repos[s['user']] = s['info']

    topmen = rank_repo(men, repos,does_size_matter,do_you_want_kids,import_loyalty, privacy) 

    boyyyss = []
    for man in topmen:
        boyyyss.append(mans[man])
    
    return boyyyss




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

        

        