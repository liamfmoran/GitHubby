import json
import gender_guesser.detector as gender

# def initial_rank():
#     pass


with open('users.dat') as data:
    d = gender.Detector()
    usrs = {}
    for line in data: 
        users = json.loads(line)
        name = users['name']
        if type(name) is str: 
            firstname = name.split()[0]
            sex = d.get_gender(firstname)
            #print(name, sex)
            if sex != 'female' and sex != 'mostly_female':
                usrs[users['name']] = 1
                
    print(usrs)
        

        