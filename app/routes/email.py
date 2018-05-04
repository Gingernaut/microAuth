
from sanic import Blueprint, response

email_bp = Blueprint("email_blueprint")


@email_bp.route("/initreset/<email>", methods=["GET", "OPTIONS"])
def initReset(email):
    try:
        accId = accFunctions.getAccIdByEmail(str(email))
        accData = accFunctions.getAccData(accId)

        if accId:
            utils.sendEmail(accData, "reset")
            return custResponse(200, "Resetting Account")

        return custResponse(400, "Invalid email for reset")

    except Exception as e:
        if app.config["DEBUG"] == True:
            print("*-*-*-*")
            print(e)
            return custResponse(400, {"Err": str(e)})
        else:
            return custResponse(400, "Error resetting email.")


@email_bp.route("/reset/<token>", methods=["GET", "OPTIONS"])
def reset(token):
    try:
        token = token.replace("*", ".")
        tokenData = jwt.decode(str(token), utils.JWT_SECRET,
                               algorithms=[utils.JWT_ALGORITHM])
        accId = int(tokenData["userId"])

        accData = accFunctions.getAccData(accId)
        accData["authToken"] = accFunctions.genToken(accId)

        return custResponse(200, "Resetting Account", accData)

    except Exception as e:
        if app.config["DEBUG"] == True:
            print("*-*-*-*")
            print(e)
            return custResponse(400, {"Err": str(e)})
        else:
            return custResponse(400, "Error resetting account.")


@email_bp.route("/confirm/<token>", methods=["GET", "OPTIONS"])
def confirm(token):
    try:
        token = token.replace("*", ".")
        tokenData = jwt.decode(str(token), utils.JWT_SECRET,
                               algorithms=[utils.JWT_ALGORITHM])
        accId = int(tokenData["userId"])
        payload = accFunctions.cleanPayload(accId, {"isValidated": True})

        if "Error" in payload:
            return custResponse(payload["errStat"], payload["Error"])

        accFunctions.updateAccount(payload)
        accData = accFunctions.getAccData(accId)
        return custResponse(200, "Successfully validated account.", accData)

    except Exception as e:
        if app.config["DEBUG"] == True:
            print("*-*-*-*")
            print(e)
            return custResponse(400, {"Err": str(e)})
        else:
            return custResponse(400, "Error validating account.")


def genEmailURL(accData, emailType):

    payload = {
        "userId": accData["id"],
        "emailAddress": accData["emailAddress"],
        "exp": pendulum.utcnow().add(days=3)
    }

    token = str(jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM).decode("utf-8"))

    customUrl = configFile["General"]["hostAddress"] + \
        "/" + emailType + "/" + token.replace(".", "*")
    return customUrl


def sendEmail(accData, templateType):

    fromEmail = configFile["SendGrid"]["SendGridFromEmail"]
    fromName = configFile["SendGrid"]["SendGridFromName"]

    for reqConfig in ["SendGridResetTemplateID", "SendGridConfirmTemplateID", "SendGridAPIKey"]:
        if not configFile["SendGrid"][reqConfig]:
            return

    if templateType.lower() == "reset":

        templateID = configFile["SendGrid"]["SendGridResetTemplateID"]
        uniqueURL = genEmailURL(accData, "reset")
        subject = str("Account Reset Link at " + fromName)

    elif templateType.lower() == "confirm":

        templateID = configFile["SendGrid"]["SendGridConfirmTemplateID"]
        uniqueURL = genEmailURL(accData, "confirm")
        subject = str("Please Confirm your account with " + fromName)

    sg = sendgrid.SendGridAPIClient(
        apikey=configFile["SendGrid"]["SendGridAPIKey"])

    from_email = sendgrid.Email(email=fromEmail, name=fromName)
    to_email = sendgrid.Email(
        email=accData["emailAddress"], name=accData.get("firstName", ""))
    content = Content("text/html", " ")
    mail = Mail(from_email=from_email, subject=subject,
                to_email=to_email, content=content)

    mail.personalizations[0].add_substitution(
        Substitution("-confirmURL-", uniqueURL))
    mail.personalizations[0].add_substitution(
        Substitution("-firstName-", accData.get("firstName", None)))
    mail.personalizations[0].add_substitution(
        Substitution("-fromName-", fromName))
    mail.set_template_id(templateID)
    sg.client.mail.send.post(request_body=mail.get())
