import requests
import string

from random import choice as randchoice, randint, randrange

# Data lists
Adjectives = open('extra/adjectives.txt',"r").readlines()
Nouns = open('extra/nouns.txt',"r").readlines()

Birthday = '1999-04-20'

def RandomString(Min, Max):
    Characters = string.ascii_letters + string.digits
    return ''.join(randchoice(Characters) for _ in range(randint(Min, Max)))

def UsernameAllowed(Username: str):
    Url = f'https://auth.roblox.com/v1/usernames/validate?request.username={Username}&request.birthday={Birthday}'
    Response = requests.get(Url, timeout=5)
    Response.raise_for_status()

    Json = Response.json()
    Code = Json.get('code')
    return Code == 0

def MakeRandomUsername(Base: str):
    # Generate an ending to stop conflicting usernames
    Max = 20 - len(Base)
    Ending = RandomString(5, Max)

    return f"{Base}{Ending}"

def MakeWordedUsername():
    # Compile a some-what realistic username
    Adjective = randchoice(Adjectives)
    Noun = randchoice(Nouns)
    Number = ""

    # Capitalization
    if randint(1,2) == 2:
        Adjective = Adjective.capitalize()
    if randint(1,2) == 2:
        Noun = Noun.capitalize()
    if randint(1,2) == 2:
        Number = str(randrange(68))

    # Word order
    Type = randint(1,3)
    if Type == 1:
        Username = Adjective + Number + Noun 
    if Type == 2:
        Username = Adjective + Noun + Number
    if Type == 3:
        Username = Noun + Adjective + Number
    if Type == 4:
        Username = Adjective + "_" + Noun + Number

    return str(Username).replace("\n","").replace("\r","")