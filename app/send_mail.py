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



template_mail_registration = env.get_template('email.html')

async def send_registration_mail(subject: str, email_to: str, body: dict):
    
    html_content = template_mail_registration.render(body)
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        template_body=html_content,
        subtype='html',
    )
    
    fm = FastMail(conf)
    await fm.send_message(message, template_name='email.html')
    return {"message": "Email has been sent."}
