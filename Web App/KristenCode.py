import core


def getMatches(preference, age, size, loyalty, attention, money, kids, privacy):
    matches = []
    hubbies, info = core.find_a_hubby()
    men = core.them_repos_though(hubbies,info, size,kids,loyalty, privacy)[0:4]

    # user = {
    #     "id" : "17077365",
    #     "name": "Jonathon",
    #     "username": "hinchley2018",
    #     "location": "College Station, TX",
    #     "email": "hinchley2018@tamu.edu"
    # }

    # matches.append(user)

    return men