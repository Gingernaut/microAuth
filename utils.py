from argon2 import PasswordHasher
import jwt, json, re, os, pendulum
import sendgrid
from sendgrid.helpers.mail import *
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


def genEmailURL(accData, emailType):

    payload = {
        "userId": accData["id"],
        "emailAddress": accData["emailAddress"],
        "exp": pendulum.utcnow().add(days=3)
    }

    token = str(jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM).decode("utf-8"))

    customUrl = configFile["General"]["hostAddress"]+ "/" + emailType + "/" + token.replace(".", "*")
    return customUrl


def sendEmail(accData, templateType):

    fromEmail = configFile["SendGrid"]["SendGridFromEmail"]
    fromName = configFile["SendGrid"]["SendGridFromName"]

    if templateType.lower() == "reset":

        templateID = configFile["SendGrid"]["SendGridResetTemplate"]
        uniqueURL = genEmailURL(accData, "reset")
        subject = str("Account Reset Link at " + fromName)
    
    elif templateType.lower() == "confirm":

        templateID = configFile["SendGrid"]["SendGridConfirmTemplate"]
        uniqueURL = genEmailURL(accData, "confirm")
        subject = str("Please Confirm your account with " + fromName)


    sg = sendgrid.SendGridAPIClient(apikey=configFile["SendGrid"]["SendGridAPIKEY"])

    from_email = sendgrid.Email(email=fromEmail, name=fromName)
    to_email = sendgrid.Email(email=accData["emailAddress"], name=accData.get("firstName",""))
    content = Content('text/html', ' ')
    mail = Mail(from_email=from_email, subject=subject, to_email=to_email, content=content)
    
    mail.personalizations[0].add_substitution(Substitution("-confirmURL-", uniqueURL))
    mail.personalizations[0].add_substitution(Substitution("-firstName-", accData.get("firstName",None)))
    mail.personalizations[0].add_substitution(Substitution("-fromName-", fromName))
    mail.set_template_id(templateID)
    sg.client.mail.send.post(request_body=mail.get())
