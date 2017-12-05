import core


def getMatches(preference, age, size, loyalty, attention, money, kids, privacy):
    matches = []
    hubbies = find_a_hubby()
    them_repos_though(hubbies,size,kids,loyalty, privacy)

    user = {
        "id" : "17077365",
        "name": "Jonathon",
        "username": "hinchley2018",
        "location": "College Station, TX",
        "email": "hinchley2018@tamu.edu"
    }

    matches.append(user)

    return matches