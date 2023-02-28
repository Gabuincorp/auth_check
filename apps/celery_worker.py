from celery import Celery
from email.header import Header
from jinja2 import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# Dependencies
from apps import services
from apps import services
from core.configurations import celery_settings

celery = Celery(__name__)
celery.conf.broker_url = celery_settings.celery_broker
celery.conf.result_backend = celery_settings.celery_backend


@celery.task(name="reset-password")
def postman_password(data: dict):
    """Render email template and send message on email with reset password"""
    template_path = "./templates/emails/test.html"
    html = open(template_path, encoding="utf-8").read()
    template = Template(html)
    recipient = data.get("recipient")
    render_template = template.render(data)
    message = MIMEMultipart()
    message["Subject"] = Header(data.get("subject"), "utf-8")
    message["To"] = recipient
    message_template = MIMEText(render_template, "html")
    message.attach(message_template)
    services.send_mail_message(recipient, message=message.as_string())


@celery.task(name="email-confirm")
def postman_email(data: dict, role: str, email: str):
    """Render email template and send message on email for email verification"""
    template_path = ""
    if role == "teacher":
        template_path = "./templates/emails/confirm.teacher.web.html"
    if role == "parent":
        template_path = "./templates/emails/confirm.parent.web.html"
    html = open(template_path, encoding="utf-8").read()
    template = Template(html)
    render_template = template.render(data)
    message = MIMEMultipart()
    message["Subject"] = Header("Confirm Email", "utf-8")
    message["To"] = email
    message_template = MIMEText(render_template, "html")
    message.attach(message_template)
    services.send_mail_message(email, message=message.as_string())
