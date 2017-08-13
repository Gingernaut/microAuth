from argon2 import PasswordHasher
import jwt, json, re, os, pendulum
from models import user, db
configFile = json.loads(open('config.json').read())

JWT_SECRET = configFile["Security"]["JWT_SECRET"]
JWT_ALGORITHM = configFile["Security"]["JWT_ALGORITHM"]

def getDBConfig():

    dbName = configFile["Database"]["dbName"]
    dbUrl = configFile["Database"]["dbUrl"]
    dbUser = configFile["Database"]["dbUser"]
    dbPass = configFile["Database"]["dbPass"]
    dbPort = configFile["Database"]["dbPort"]

    return "postgresql://" + dbUser + ":" + dbPass + "@" + dbUrl + "/" + dbName


def isValidEmail(emailAddr):
    if not re.match(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}\b", emailAddr):
        return False
    return True

def isValidPass(password):
    return len(str(password)) >= int(configFile["Security"]["minPassLength"])


def encryptPass(password):
    ph = PasswordHasher()
    return ph.hash(password)

# do this on the account class?
def passMatches(accountPass, postPass):
    try:
        ph = PasswordHasher()
        ph.verify(accountPass, postPass)

        return True
    except:
        return False

# https://github.com/daviddrysdale/python-phonenumbers
def validPhone(phonenum):

    numdigits = len(str(phonenum))

    if numdigits > 12 or numdigits < 10:
        return False
    return True

