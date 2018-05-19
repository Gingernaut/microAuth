
from sanic import Blueprint, response
from utils import utils
from config import get_config
import jwt

appConfig = get_config()

email_bp = Blueprint("email_blueprint")

"""
POST /confirm-email/:token
POST /reset-password/:emailAddress
"""


@email_bp.route("/reset-password/<emailAddress>", methods=["POST"])
async def get(request, emailAddress):
    try:
        user = utils.get_account_by_email(emailAddress)
        if not user:
            return response.json({"error": "User not found"}, 404)

        # Send reset email

        return response.json(user.serialize(), 200)
    except Exception as e:
        res = {"error": "Email reset failed"}
        if request.app.config["API_ENV"] != "PRODUCTION":
            res["detailed"] = str(e)
        return response.json(res, 500)


@email_bp.route("/confirm-reset/<token>", methods=["POST"])
def reset(request, token):

    token = token.replace("*", ".")
    tokenData = jwt.decode(
        str(token), appConfig.JWT_SECRET, algorithms=[appConfig.JWT_ALGORITHM]
    )
    accId = int(tokenData["userId"])

    accData = accFunctions.getAccData(accId)
    accData["authToken"] = accFunctions.genToken(accId)

    return custResponse(200, "Resetting Account", accData)


@email_bp.route("/confirm-email/<token>", methods=["POST"])
def confirm(token):
    token = token.replace("*", ".")
    tokenData = jwt.decode(
        str(token), utils.JWT_SECRET, algorithms=[utils.JWT_ALGORITHM]
    )
    accId = int(tokenData["userId"])
    payload = accFunctions.cleanPayload(accId, {"isValidated": True})

    if "Error" in payload:
        return custResponse(payload["errStat"], payload["Error"])

    accFunctions.updateAccount(payload)
    accData = accFunctions.getAccData(accId)
    return custResponse(200, "Successfully validated account.", accData)

    payload = {
        "userId": accData["id"],
        "emailAddress": accData["emailAddress"],
        "exp": pendulum.utcnow().add(days=3),
    }

    token = str(jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM).decode("utf-8"))

    customUrl = (
        configFile["General"]["hostAddress"]
        + "/"
        + emailType
        + "/"
        + token.replace(".", "*")
    )
    return customUrl


def sendEmail(accData, templateType):

    fromEmail = configFile["SendGrid"]["SendGridFromEmail"]
    fromName = configFile["SendGrid"]["SendGridFromName"]

    for reqConfig in [
        "SendGridResetTemplateID",
        "SendGridConfirmTemplateID",
        "SendGridAPIKey",
    ]:
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

    sg = sendgrid.SendGridAPIClient(apikey=configFile["SendGrid"]["SendGridAPIKey"])

    from_email = sendgrid.Email(email=fromEmail, name=fromName)
    to_email = sendgrid.Email(
        email=accData["emailAddress"], name=accData.get("firstName", "")
    )
    content = Content("text/html", " ")
    mail = Mail(
        from_email=from_email, subject=subject, to_email=to_email, content=content
    )

    mail.personalizations[0].add_substitution(Substitution("-confirmURL-", uniqueURL))
    mail.personalizations[0].add_substitution(
        Substitution("-firstName-", accData.get("firstName", None))
    )
    mail.personalizations[0].add_substitution(Substitution("-fromName-", fromName))
    mail.set_template_id(templateID)
    sg.client.mail.send.post(request_body=mail.get())
