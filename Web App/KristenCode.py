def getMatches(preference, age, size, loyalty, attention, money, kids, privacy):
    matches = []
    #This the format of a user. Just append all of the matches to the list and the front end does the rest.
    user = {
        "id" : "17077365",
        "name": "Jonathon",
        "username": "hinchley2018",
        "location": "College Station, TX",
        "email": "hinchley2018@tamu.edu"
    }

    matches.append(user)

    return matches