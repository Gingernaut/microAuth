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

def createAdmin():
    email = "root@root.com"
    passw = "1234567"
    userRole = "ADMIN"

    admin = user(emailAddress=email,
                password=encryptPass(passw),
                userRole=userRole)
    
    db.session.add(admin)
    db.session.commit()

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

def signin(email, passw):

    try:
        account = getAccountbyEmail(email)
        encryptedPass = account.password

        if passMatches(encryptedPass, passw):
            return account.id

    except Exception as e:
        print(e)
    
    return None

def createAccount(payload):

    try:
        newAcc = user(
            emailAddress=payload["emailAddress"],
            password=payload["password"],
            firstName=payload["firstName"],
            lastName=payload["lastName"]
        )
        db.session.add(newAcc)
        db.session.commit()

        return newAcc.id
    except Exception as e:
        print('****')
        print(e)
        return None

def updateAccount(payload):
    account = getAccountbyID(payload["id"])
    account.modifiedDate = pendulum.utcnow()

    if "firstName" in payload:
        account.firstName = payload["firstName"]

    if "lastName" in payload:
        account.lastName = payload["lastName"]
    
    if "emailAddress" in payload:
        account.emailAddress = payload["emailAddress"]

    if "password" in payload:
        account.password = payload["password"]

    if "phoneNumber" in payload:
        account.phoneNumber = payload["phoneNumber"]

    if "userRole" in payload:
        account.userRole = payload["userRole"]
    
    if "isValidated" in payload:
        account.isValidated = payload["isValidated"]

    db.session.commit()
    
    
def genToken(accId):
    account = getAccountbyID(accId)
    return account.genToken()

def getAccData(accId):
    
    account = getAccountbyID(accId)
    return account.serialize()

def isAdmin(accId):
    try:
        return getAccountbyID(accId).userRole == "ADMIN"
    except:
        return False

def getAccountbyID(AccID):

    return user.query.filter_by(id=AccID).first()

def getAccountbyEmail(emailAddr):

    return user.query.filter_by(emailAddress=emailAddr).first()

def accountExists(postEmail):

    return getAccountbyEmail(postEmail) != None

def getIdFromToken(jwt_token):

    try:
        payload = jwt.decode(str(jwt_token), JWT_SECRET, algorithms=[JWT_ALGORITHM])
        userId = int(payload["userId"])
        acc = getAccountbyID(userId)

        if acc:
            return acc.id
        else:
            return None
    except:
        return None