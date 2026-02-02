import requests

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from core.email_utils import send_email_by_context



class ContactPageView(TemplateView):
    """
    View for rendering and handling the contact page.
    """
    template_name = "contact.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "CLOUDFLARE_TURNSTILE_SITE_KEY": settings.CLOUDFLARE_TURNSTILE_SITE_KEY,
        })
        return context

    def verify_turnstile(self, token, remote_ip=None):
        """
        Verify Cloudflare Turnstile token server-side.
        """
        payload = {
            "secret": settings.CLOUDFLARE_TURNSTILE_SECRET_KEY,
            "response": token,
        }

        if remote_ip:
            payload["remoteip"] = remote_ip

        response = requests.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data=payload,
            timeout=5,
        )

        result = response.json()
        return result.get("success", False)

    def post(self, request):
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        message = request.POST.get("message")

        if not all([name, phone, email, message]):
            messages.error(request, "Please fill in all the fields.")
            return render(request, self.template_name, self.get_context_data())

        # Cloudflare Turnstile token
        turnstile_token = request.POST.get("cf-turnstile-response")

        if not turnstile_token:
            messages.error(request, "Captcha verification failed. Please try again.")
            return render(request, self.template_name, self.get_context_data())

        if not self.verify_turnstile(turnstile_token, request.META.get("REMOTE_ADDR")):
            messages.error(request, "Captcha verification failed. Please try again.")
            return render(request, self.template_name, self.get_context_data())

        # CAPTCHA passed — send emails
        subject = f"CodeBlock Contact Message from {name}"
        message_content = (
            f"Sender's Name: {name}\n"
            f"Sender's Phone: {phone}\n"
            f"Sender's Email: {email}\n\n"
            f"Message:\n{message}"
        )

        def send_email_to_user(recipient_email):
            send_email_by_context(
                subject=subject,
                message=message_content,
                recipient_list=[recipient_email],
                context='company'
            )

        # Send to main contact address
        send_email_to_user(settings.DEFAULT_FROM_EMAIL)

        # Send to all users with email addresses
        for user in User.objects.exclude(email="").only("email"):
            send_email_to_user(user.email)

        messages.success(request, "Your message has been sent successfully!")
        return render(request, self.template_name, self.get_context_data())
