import json
import math
import gender_guesser.detector as gender
import sys
import os
import statistics

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

def normalizer(x, maxval, minval):
    val = int((x-minval)/(maxval-minval)*5)+1
    return 5 if val > 5 else val

def normalize(x, max, min):
    if(x > max):
        x = max
    value = (int((x-min)/(max-min)))
    return int((x-min)/(max-min))+2



#TO DO: modify to query repo table
def languages(languages, mate):
    all_langs = {}
    vals = []
    for language in languages:
        rating = 0
        if len(languages) == 0:
            rating = 1
            mates[person].append(rating)
            continue
        if language not in all_langs:
                all_langs[language] = 0
        all_langs[language] +=1
        if len(all_langs) > 1:
            var = statistics.variance([all_langs[x] for x in all_langs],statistics.mean([all_langs[x] for x in all_langs]))
            vals.append(var)

    if len(vals) > 1:
        maxval = max(vals)
        minval = min(vals)

        # print(':', val, maxval, minval, normalizer(val, maxval, minval))
        vals = [normalizer(val, maxval, minval) for val in vals]

        for val in vals:
            print(val)

        # vals = [normalizer(x, maxval, minval) for x in vals]

    # for val in vals:
    #   print('val:', val)


    # print('mate: ',mate)
    # print(all_langs)

        # his_langs = {}
        # for i in info[person]:
        #     if i not in his_langs:
        #         his_langs[i] = 0
        #     his_langs[i] +=1
        # sum1 = 0
        # for l in his_langs:
        #     sum1 += his_langs[l]
        # mean = float(sum1)/len(his_langs)
        # tots = 0
        # for l in his_langs:
        #     tots += (his_langs[l]-mean)**2
        # var = float(tots)+1/len(his_langs)
        # var = logistic(var)
        # men[person] += var
          
        

    

#TO DO: modify to query repo table
def rank_repo(mates,info,size,loyalty,kids):
    sizes = {}
    dum = 0
    loyalty = {}
    for person in mates:
        person_size = 0
        person_languages = []
        repos = info[person][19]
        ## Does Size Matter?
        ## Gets total line size of all commits a user has made and returns a rank of 1-5
        ## Size is index 0 of score vector
        for repo in repos:
            person_languages.append(repo[16])
            repo_data = json.loads(repo[10])
            for data in repo_data:
                person_size += data['stats']['total']
        sizes[person] = person_size
    max_size = statistics.mean([sizes[m] for m in sizes])
    min_size = min([sizes[m] for m in sizes])
    languages(person_languages,mates[person])
    for m in sizes:
        if sizes[m] == 0:
            rating = 1
        else:
            rating = normalize(sizes[m],max_size,min_size)
        mates[m].append(rating)
    ##Now Sizes has been added to the features vector, Next Loyalty. 
    

            
        
    #         for l in test:
    #             ## DOES SIZE MATTER 'YES' OR 'NO' (NO WILL BE A 1 AND YES WILL BE A 5)
    #             size = l['stats']['total']
    #             stff[person] += size
    #             num_repos += 1
    #             dum += size
    #             repo_length = l['length']
    #         ##DO YOU WANT KIDS 'YES' OR 'NO' (NO WILL BE A 1 AND YES WILL BE A 5)
    #         fork_count = info[person][1]

    #         #open_issues = info[person][2]
    #         #stargazers_count = info[person][3]
    #         his_langs.append(info[person][4])
    #     ##HOW IMPORTABT IS PRIVACY == NUM OF HIS REPOS
    #     stff[person] = float(stff[person])/num_repos

    #     ##HOW IMPORTANT IS LOYALTY == LANGUAGE VARIANCE
    #     loyalty[person] = his_langs
    # ## DOES SIZE MATTER?! 
    # if does_size_matter == 'yes':
    #     mean = dum/len(stff)
    #     for guy in stff:
    #         if stff[guy] < mean :
    #             men[guy] -= 1
    #         if stff[guy] > mean :
    #             men[guy] +=1 
    # ## HOW IMPORTANT IS LOYALTY
    #     languages(men, loyalty, import_loyalty)
    # res = dict((v, k) for k, v in men.items())
    # sort = sorted(res, reverse=True)[:10]
    # retval = [ { "id": res[guyd] for guyd in sort } ]
    # return [ res[x] for x in sorted(res, reverse=True)[:10] ]



def find_a_hubby(preference,size,loyalty,kids):
    """Queries BigQuery and gets data from men and initalizes score."""
    # TODO: I think BigQuery.queryall can just be called now wihch will sort by gender
    # NOTE: The above should only be done if the local dictionaries are empty
    
    bq = bigquery.BigQuery()
    male, female = bq.queryall()
    mates = {}
    ## [SIZE, LOYALTY, KIDS]
    features = []
    if preference == 'male':
        for m in male:
            mates[m] = []
            rank_repo(mates,male,size,loyalty,kids)
    else:
        for f in female:
            mates[f] = []
            rank_repo(mates,female,size,loyalty,kids)
    

##USED FOR BIG QUERY PARSING IGNORE FOR NOW 

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
print(find_a_hubby('female',5,5,5))
##GOT ALL INFO FROM REPOS, CAN NOW DO OFFLINE ANALYSIS FOR HUBBY SCORE
##GOT DATA NEEDED FOR HUBBIES OTHER FEATURES, CAN NOW COMPUTE OFFLINE SCORE.
##LET'S EFFING GO

        

        