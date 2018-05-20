
import os
import sendgrid
from sendgrid.helpers.mail import *
from config import get_config
from pathlib import Path
import codecs

email_path = Path.cwd() / "email-templates"

appConfig = get_config()
sg = sendgrid.SendGridAPIClient(apikey=appConfig.SENDGRID_API_KEY)


def send_reset_email(user, reset):

    def build_reset_email():
        return ""

    return ""


def send_welcome_email(user):

    def build_welcome_email():
        welcome_email = open(f"{email_path}/welcome-email.html", "r").read()

        welcome_email = welcome_email.replace("{{from_org}}", appConfig.FROM_ORG_NAME)
        welcome_email = welcome_email.replace(
            "{{login_url}}", f"{appConfig.FROM_WEBSITE_URL}/login"
        )
        welcome_email = welcome_email.replace(
            "{{action_url}}", f"{appConfig.FROM_WEBSITE_URL}/confirm/{user.UUID}"
        )

        name = user.firstName
        if not name:
            name = user.emailAddress
        welcome_email = welcome_email.replace("{{name}}", name)

        from_email = Email(appConfig.FROM_EMAIL)
        to_email = Email(user.emailAddress)
        subject = f"Please confirm your account with {appConfig.FROM_ORG_NAME}"
        content = Content("text/html", welcome_email)

        return Mail(from_email, subject, to_email, content)

    mail = build_welcome_email()
    sg.client.mail.send.post(request_body=mail.get())
