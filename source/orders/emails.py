# orders/emails.py
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.utils.timezone import now

from core.email_utils import send_email_by_context
from branding.models import Branding
from core import settings


# ----------------------------------
# ORDER CONFIRMATION EMAILS
# ----------------------------------

def send_order_emails(order, *, force=False):
    if order.emails_sent_at and not force:
        return

    branding = Branding.objects.first()
    if not branding:
        raise RuntimeError("Branding configuration is missing")

    base_context = {
        "order": order,
        "branding": branding,
         "site_url": settings.SITE_URL,
    }

    # Customer email
    customer_html = render_to_string(
        "order_email.html",
        {**base_context, "is_admin": False}
    )

    send_email_by_context(
        subject=f"Your order {order.reference}",
        message="Thank you for your order.",
        recipient_list=[order.email],
        html_message=customer_html,
    )

    # Admin notification
    admins = get_user_model().objects.filter(
        is_staff=True,
        is_active=True,
    ).exclude(email="")

    if admins.exists():
        admin_html = render_to_string(
            "order_email.html",
            {**base_context, "is_admin": True}
        )

        send_email_by_context(
            subject=f"New order {order.reference}",
            message="New order received.",
            recipient_list=[u.email for u in admins],
            html_message=admin_html,
        )

    order.emails_sent_at = now()
    order.save(update_fields=["emails_sent_at"])


# ----------------------------------
# SHIPPING EMAIL
# ----------------------------------

def send_shipping_email(order):
    if not hasattr(order, "shipment"):
        raise RuntimeError(
            f"Cannot send shipping email: Order {order.reference} has no shipment"
        )
    
    branding = Branding.objects.first()
    if not branding:
        raise RuntimeError("Branding configuration is missing")

    shipment = order.shipment

    context = {
        "order": order,
        "shipment": shipment,
        "branding": branding,
        "site_url": settings.SITE_URL,
    }

    html = render_to_string(
        "order_shipped_email.html",
        context,
    )

    send_email_by_context(
        subject=f"Your order {order.reference} has shipped",
        message="Your order is on the way.",
        recipient_list=[order.email],
        html_message=html,
    )
