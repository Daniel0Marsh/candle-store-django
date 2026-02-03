# basket/views.py
from decimal import Decimal
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.conf import settings
from django.db import transaction
import stripe
import json

from branding.models import Branding
from home.models import HomePage
from products.models import Product, ProductSettings
from django.contrib.auth import get_user_model

from .utils import calculate_basket
from orders.services import create_order_from_basket
from orders.models import Order


stripe.api_key = settings.STRIPE_SECRET_KEY


class UserDetailsPageView(TemplateView):
    """
    Collect user contact and address details before Stripe checkout.
    """
    template_name = 'user_details.html'

    def get_context_data(self, **kwargs):
        basket = self.request.session.get('basket', {})
        cart_info = calculate_basket(basket)

        # Calculate remaining for free delivery
        pricing_settings = cart_info.get('pricing_settings', None)
        if pricing_settings and not cart_info['free_delivery_applied']:
            remaining = pricing_settings.free_delivery_over - cart_info['total']
            cart_info['remaining_for_free_delivery'] = remaining if remaining > 0 else 0

        context = {
            "cart": cart_info,
        }
        return context

    def post(self, request, *args, **kwargs):
        user_info = {
            'full_name': request.POST.get('full_name'),
            'email': request.POST.get('email'),
            'address_line1': request.POST.get('address_line1'),
            'address_line2': request.POST.get('address_line2', ''),
            'city': request.POST.get('city'),
            'postal_code': request.POST.get('postal_code'),
            'country': request.POST.get('country')
        }
        request.session['user_info'] = user_info
        return redirect('stripe_payment')


class BasketPageView(TemplateView):
    template_name = 'basket.html'

    def get_context_data(self, **kwargs):
        basket = self.request.session.get('basket', {})
        basket_info = calculate_basket(basket)
        context = super().get_context_data(**kwargs)
        context.update({
            "cart": basket_info,
        })
        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        product_id = request.POST.get('product_id')
        basket = request.session.get('basket', {})

        if action == 'remove':
            basket.pop(product_id, None)
        elif action == 'update':
            quantity = int(request.POST.get('quantity', 1))
            if quantity <= 0:
                basket.pop(product_id, None)
            else:
                basket[product_id] = quantity

        request.session['basket'] = basket
        return redirect('basket')


class StripePaymentView(TemplateView):
    template_name = 'stripe_payment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        basket = self.request.session.get('basket')
        user_info = self.request.session.get('user_info')

        if not basket or not user_info:
            return redirect("basket")

        basket_info = calculate_basket(basket)
        currency = getattr(settings, "STORE_CURRENCY", "GBP").lower()

        # -----------------------------
        # CREATE ORDER (PENDING)
        # -----------------------------
        order = create_order_from_basket(
            basket=basket,
            user_info=user_info,
            pricing=basket_info,
        )

        # Store for confirmation page
        self.request.session["order_id"] = order.id

        # -----------------------------
        # STRIPE LINE ITEMS
        # -----------------------------
        line_items = []

        for item in basket_info["products"]:
            line_items.append({
                "price_data": {
                    "currency": currency,
                    "unit_amount": int(item["product"].effective_price * 100),
                    "product_data": {
                        "name": item["product"].title,
                    },
                },
                "quantity": item["quantity"],
            })

        if basket_info["delivery_fee"] > 0:
            line_items.append({
                "price_data": {
                    "currency": currency,
                    "unit_amount": int(basket_info["delivery_fee"] * 100),
                    "product_data": {
                        "name": "Delivery Fee",
                    },
                },
                "quantity": 1,
            })

        # -----------------------------
        # STRIPE SESSION
        # -----------------------------
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            line_items=line_items,
            success_url="http://localhost:8000/checkout/success/",
            cancel_url="http://localhost:8000/basket/",
            metadata={
                "order_id": str(order.id),
                "order_reference": order.reference,
            },
        )

        context.update({
            "session_id": session.id,
            "publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
        })

        return context


class PaymentConfirmationView(TemplateView):
    template_name = "payment_confirmation.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        order_id = self.request.session.get("order_id")
        if not order_id:
            return context

        try:
            order = Order.objects.get(pk=order_id, status="paid")
        except Order.DoesNotExist:
            return context

        # CLEAR SESSION DATA
        for key in ("basket", "user_info", "order_id"):
            self.request.session.pop(key, None)

        self.request.session.modified = True
        context["order"] = order
        return context
