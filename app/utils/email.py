import sendgrid
from sendgrid.helpers.mail import Mail
from models.reset import PasswordReset as ResetModel
from models.user import User as UserModel

from config import get_config
from pathlib import Path

email_path = Path.cwd() / "email-templates"

appConfig = get_config()
sg = sendgrid.SendGridAPIClient(appConfig.SENDGRID_API_KEY)


def send_confirmation_email(user: UserModel, reset: ResetModel):
    def build_mail():
        welcome_email = open(f"{email_path}/welcome-email.html", "r").read()

        welcome_email = welcome_email.replace("__FROM_ORG__", appConfig.FROM_ORG_NAME)
        welcome_email = welcome_email.replace(
            "__ACTION_URL__",
            f"{appConfig.FROM_WEBSITE_URL}/confirm-account/{reset.gen_token()}",
        )

        name = user.firstName
        if not name:
            name = user.emailAddress
        welcome_email = welcome_email.replace("__NAME__", name)

        return Mail(
            from_email=appConfig.FROM_EMAIL,
            to_emails=user.emailAddress,
            subject=f"Please confirm your account with {appConfig.FROM_ORG_NAME}",
            html_content=welcome_email,
        )

    mail = build_mail()
    sg.send(mail)


def send_reset_email(user: UserModel, reset: ResetModel):
    def build_mail():

        reset_email = open(f"{email_path}/password-reset.html", "r").read()
        reset_email = reset_email.replace("__FROM_ORG__", appConfig.FROM_ORG_NAME)
        reset_email = reset_email.replace(
            "__TTL_HRS__", str(appConfig.PASSWORD_RESET_LINK_TTL_HOURS)
        )
        reset_email = reset_email.replace(
            "__ACTION_URL__", f"{appConfig.FROM_WEBSITE_URL}/reset/{reset.gen_token()}"
        )

        reset_email = reset_email.replace(
            "__WEBSITE_URL__", f"{appConfig.FROM_WEBSITE_URL}/"
        )

        name = user.firstName
        if not name:
            name = user.emailAddress
        reset_email = reset_email.replace("__NAME__", name)

        return Mail(
            from_email=appConfig.FROM_EMAIL,
            to_emails=user.emailAddress,
            subject=f"Password reset requested at {appConfig.FROM_ORG_NAME}",
            html_content=reset_email,
        )

    mail = build_mail()
    sg.send(mail)
