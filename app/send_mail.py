from fastapi import APIRouter
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jinja2 import Environment, FileSystemLoader
from .config_mail import setting

router = APIRouter()

# Налаштування конфігурації
conf = ConnectionConfig(
    MAIL_USERNAME=setting.mail_username,
    MAIL_PASSWORD=setting.mail_password,
    MAIL_FROM=setting.mail_from,
    MAIL_PORT=setting.mail_port,
    MAIL_SERVER=setting.mail_server,
    MAIL_FROM_NAME=setting.mail_from_name,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,  
)


# # Налаштування Jinja2
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('password_reset.html')

async def password_reset(subject: str, email_to: str, body: dict):
    """
    This function is used to send a password reset email to the user.

    Args:
        subject (str): The subject of the email.
        email_to (str): The email address of the user.
        body (dict): The body of the email, which includes the reset link.

    Returns:
        dict: A dictionary containing a message indicating that the email was sent.

    Raises:
        Exception: An exception is raised if there is an error sending the email.
    """

    html_content = template.render(body)

    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=html_content,
        subtype="html",
    )

    fm = FastMail(conf)
    await fm.send_message(message, template_name='password_reset.html')

    return {"message": "Email has been sent."}

templare_mail_regostration = env.get_template('email.html')

async def send_registration_mail(subject: str, email_to: str, body: dict):
    """
    This function is used to send a registration email to the user.

    Args:
        subject (str): The subject of the email.
        email_to (str): The email address of the user.
        body (dict): The body of the email, which includes the activation link.

    Returns:
        dict: A dictionary containing a message indicating that the email was sent.

    Raises:
        Exception: An exception is raised if there is an error sending the email.
    """
    
    html_content = templare_mail_regostration.render(body)
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        template_body=html_content,
        subtype='html',
    )
    
    fm = FastMail(conf)
    await fm.send_message(message, template_name='email.html')
