# orders/webhooks.py
import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Order
from .services import mark_order_as_paid
from .emails import send_order_emails


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET,
        )
    except Exception:
        # Invalid signature or payload
        return HttpResponse(status=400)

    # -------------------------
    # CHECKOUT COMPLETED
    # -------------------------
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        metadata = session.get("metadata") or {}
        order_id = metadata.get("order_id")
        payment_intent = session.get("payment_intent")

        # Stripe CLI test events often have no metadata
        if not order_id:
            return HttpResponse(status=200)

        try:
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            # Order deleted or already processed
            return HttpResponse(status=200)

        mark_order_as_paid(order, payment_intent)
        send_order_emails(order)

    # Always acknowledge Stripe
    return HttpResponse(status=200)
