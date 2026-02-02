"""
Email utility functions for handling multiple email configurations
"""
from django.core.mail import EmailMessage
from django.conf import settings


def send_company_email(subject, message, recipient_list, html_message=None):
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipient_list,
    )

    if html_message:
        email.content_subtype = "html"
        email.body = html_message

    return email.send()


def send_email_by_context(subject, message, recipient_list, html_message=None):
    return send_company_email(subject, message, recipient_list, html_message)
