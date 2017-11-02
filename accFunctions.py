import jwt, json, pendulum
from models import user, db
import utils

configFile = json.loads(open("config.json").read())
JWT_SECRET = configFile["Security"]["JWT_SECRET"]
JWT_ALGORITHM = configFile["Security"]["JWT_ALGORITHM"]

def createAdmin():
    try:
        print("Creating Admin Account")
        admin = user(emailAddress=configFile["Security"]["initEmail"],
                    password=utils.encryptPass(configFile["Security"]["initPass"]),
                    userRole="ADMIN",
                    isValidated=True)
        
        db.session.add(admin)
        db.session.commit()
    except Exception as e:
        print("*-*-*-*")
        print(e)
        pass

def signin(email, passw):

    try:
        account = getAccountByEmail(email)
        encryptedPass = account.password

        if utils.passMatches(encryptedPass, passw):
            return account.id

    except Exception as e:
        print("****")
        print(e)
    
    return None

def createAccount(payload):
    try:
        newAcc = user(
            emailAddress=payload["emailAddress"],
            password=payload["password"],
            firstName=payload["firstName"],
            lastName=payload["lastName"])

        db.session.add(newAcc)
        db.session.commit()

        return newAcc.id
    except Exception as e:
        print("****")
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

def getAccountByEmail(emailAddr):
    return user.query.filter_by(emailAddress=emailAddr).first()

def getAccIdByEmail(emailAddr):
    return getAccountByEmail(emailAddr).id or None


def accountExists(postEmail):
    return getAccountByEmail(postEmail) != None

def deleteAccount(accId):
    try:
        acc = getAccountbyID(accId)
        db.session.delete(acc)
        db.session.commit()
        return True
    except:
        return False


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

def cleanPayload(accId, res):
        payload = {"id": accId}
        
        if not res:
            return {"errStat": 400, "Error": "data required for update"}

        if res.get("emailAddress", None):
            if not utils.isValidEmail(res["emailAddress"]):
                return {"errStat": 400, "Error": "Invalid email address."}

            if getAccData(accId)["emailAddress"] != res["emailAddress"] and accountExists(res["emailAddress"]):
                return {"errStat": 400, "Error": "Another account exists already with that email. Update not allowed."}

            payload["emailAddress"] =res["emailAddress"].lower()

        if res.get("firstName", None):
            payload["firstName"] = res["firstName"].title()
        
        if res.get("lastName", None):
            payload["lastName"] = res["lastName"].title()

        if res.get("password", None):
            payload["password"] = utils.encryptPass(res["password"])

        if res.get("phoneNumber", None):
            payload["phoneNumber"] == res["phoneNumber"]

        if res.get("isValidated", None):
            payload["isValidated"] = True if res["isValidated"] == "True" else False
        
        return payload
