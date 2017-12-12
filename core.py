import json
import math
import gender_guesser.detector as gender
import sys
import os
import statistics
from collections import Counter

sys.path.insert(0, './crawler/')

import bigquery


def eucliddist(a, b):
    total = 0
    zipped = zip(a, b)

    for tup in zipped:
        total += (tup[0] - tup[1]) ** 2

    return total ** (1/2)


def langaugesalary(language):
    salaries = {
        'Java': 130,
        'Objective-C': 112,
        'Python': 105,
        'C++': 102,
        'Perl': 100,
        'C': 100,
        'R': 99,
        'JavaScript': 92,
        'CoffeeScript': 82,
        'Ruby': 89,
        'HTML': 60,
        'PHP': 89,
        'C#': 89,
        'Swift': 115,
        'SQL': 80 
    }

    if language not in salaries:
        return 84

    return salaries[language]


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


def logistic(x, maxnnum):
    """Normalizes a value to be between 1 and maxnum."""
    val = maxnum / (1 + math.exp(-x))
    return int(val+1)

def normalizer(x, maxval, minval):
    if maxval == minval:
        return 5
    val = int((x-minval)/(maxval-minval)*5)+1
    return 5 if val > 5 else val

def normalize(x, max, min):
    if(x > max):
        x = max
    value = (int((x-min)/(max-min)))
    return int((x-min)/(max-min))+2


def getsalary(languages):
    if len(languages) == 0:
        return 84
    langauge, _ = Counter(languages).most_common(1)[0]
    return langaugesalary(langauge)


#TO DO: modify to query repo table
def languages(languages, mate):
    all_langs = {}
    for language in languages:
        rating = 0
        if len(languages) == 0:
            return 1
        if language not in all_langs:
                all_langs[language] = 0
        all_langs[language] +=1
    if len(all_langs) > 1:
        var = statistics.variance([all_langs[x] for x in all_langs],statistics.mean([all_langs[x] for x in all_langs]))
    else:
        return 5
    return var

def rank_repo(mates,info):
    sizes = {}
    variances = {}
    salaries = {}
    dum = 0
    loyalty = {}
    forks = {}
    num_repos = {}
    for person in mates:
        person_size = 0
        person_forks = 0
        person_repos = 0
        person_languages = []
        repos = info[person][19]
        ## Does Size Matter?
        ## Gets total line size of all commits a user has made and returns a rank of 1-5
        ## Size is index 0 of score vector
        for repo in repos:
            person_repos += 1
            person_languages.append(repo[16])
            repo_data = json.loads(repo[10])
            person_forks += repo[18]
            for data in repo_data:
                person_size += data['stats']['total']
        sizes[person] = person_size
        variances[person] = languages(person_languages,mates[person])
        salaries[person] = getsalary(person_languages)
        forks[person] = person_forks
        num_repos[person] = person_repos
    max_size = statistics.mean([sizes[m] for m in sizes])
    min_size = min([sizes[m] for m in sizes])
    for m in sizes:
        if sizes[m] == 0:
            rating = 1
        else:
            rating = normalize(sizes[m],max_size,min_size)
        mates[m].append(rating)
    ##Now Sizes has been added to the features vector, Next Loyalty
    max_var = max([variances[x] for x in variances])
    min_var = min([variances[x] for x in variances])
    for v in variances:
        mates[v].append(6-normalizer(variances[v],max_var,min_var))

    ##Kids, also known as Fork_Count
    for f in forks:
        if forks[f] > 0:
            mates[f].append(5)
        else:
            mates[f].append(1)

    max_sal = max([salaries[x] for x in salaries])
    min_sal = min([salaries[x] for x in salaries])
    for s in salaries:
        mates[s].append(normalizer(salaries[s], max_sal, min_sal))
    
    max_rep = max([num_repos[x] for x in num_repos])
    min_rep = min([num_repos[x] for x in num_repos])
    for r in num_repos:
        mates[r].append(normalizer(num_repos[r],max_rep,min_rep))
    return mates

def find_a_hubby(preference,size,loyalty,kids,salary,attention):
    """Queries BigQuery and gets data from men and initalizes score."""

    users_choices = []
    users_choices.append(5 if size == 'Yes' else 1)
    users_choices.append(int(loyalty))
    users_choices.append(5 if kids == 'Yes' else 1)
    users_choices.append(int(salary))
    users_choices.append(int(attention))

    print(users_choices)
    print(preference)

    male, female = bq.queryall()
    mates = {}
    distances = {}
    ## [SIZE, LOYALTY, KIDS, SALARY, ATTENTION]

    users = None
    
    if preference == 'man':
        for m in male:
            mates[m] = []
        rank_repo(mates,male)
        users = male
    else:
        for f in female:
            mates[f] = []
        rank_repo(mates,female)
        users = female
    for mate in mates:
        dist = eucliddist(mates[mate], users_choices)
        distances[mate] = dist
    top = sorted(distances.items(), key=lambda x: x[1])[:10]

    retval = []

    for user in top:
        val = {}
        val['id'] = users[user[0]][0]
        val['name'] = users[user[0]][9]
        val['username'] = users[user[0]][1]
        val['location'] = users[user[0]][12]
        val['email'] = 'email@gmail.com'
        retval.append(val)

    return retval
