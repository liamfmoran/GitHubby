import sys

sys.path.insert(0, './../')

import core


def getMatches(preference, age, size, loyalty, attention, money, kids, privacy):
    matches = core.find_a_hubby(preference, size, loyalty, kids, money, attention)[:5]

    # user = {
    #     "id" : "17077365",
    #     "name": "Jonathon",
    #     "username": "hinchley2018",
    #     "location": "College Station, TX",
    #     "email": "hinchley2018@tamu.edu"
    # }

    # matches.append(user)

    return matches