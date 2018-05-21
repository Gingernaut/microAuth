import sendgrid
from sendgrid.helpers.mail import Email, Content, Mail
from config import get_config
from pathlib import Path

email_path = Path.cwd() / "email-templates"

appConfig = get_config()
sg = sendgrid.SendGridAPIClient(apikey=appConfig.SENDGRID_API_KEY)


def send_reset_email(user, reset):

    def build_reset_email():

        reset_email = open(f"{email_path}/password-reset.html", "r").read()
        reset_email = reset_email.replace("{{from_org}}", appConfig.FROM_ORG_NAME)
        reset_email = reset_email.replace(
            "{{ttl}}", str(appConfig.PASSWORD_RESET_LINK_TTL_HOURS)
        )
        reset_email = reset_email.replace(
            "{{action_url}}", f"{appConfig.FROM_WEBSITE_URL}/confirm-reset/{reset.UUID}"
        )

        name = user.firstName
        if not name:
            name = user.emailAddress
        reset_email = reset_email.replace("{{name}}", name)

        from_email = Email(appConfig.FROM_EMAIL)
        to_email = Email(user.emailAddress)
        subject = f"Password reset requested at {appConfig.FROM_ORG_NAME}"
        content = Content("text/html", reset_email)

        return Mail(from_email, subject, to_email, content)

    mail = build_reset_email()
    sg.client.mail.send.post(request_body=mail.get())


def send_welcome_email(user):

    def build_welcome_email():
        welcome_email = open(f"{email_path}/welcome-email.html", "r").read()

        welcome_email = welcome_email.replace("{{from_org}}", appConfig.FROM_ORG_NAME)
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
