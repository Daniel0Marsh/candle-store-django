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
from core.email_utils import send_email_by_context
from django.template.loader import render_to_string


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
        basket = self.request.session.get('basket', {})
        user_info = self.request.session.get('user_info', {})

        basket_info = calculate_basket(basket)
        currency = getattr(settings, "STORE_CURRENCY", "GBP").lower()

        line_items = []
        # Add products
        for item in basket_info['products']:
            line_items.append({
                'price_data': {
                    'currency': currency,
                    'unit_amount': int(item['product'].effective_price * 100),
                    'product_data': {'name': item['product'].title},
                },
                'quantity': item['quantity'],
            })
        # Add delivery fee if applicable
        if basket_info['delivery_fee'] > 0:
            line_items.append({
                'price_data': {
                    'currency': currency,
                    'unit_amount': int(basket_info['delivery_fee'] * 100),
                    'product_data': {'name': 'Delivery Fee'},
                },
                'quantity': 1,
            })

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url='http://localhost:8000/checkout/success/',
            cancel_url='http://localhost:8000/basket/',
            metadata={
                'email': user_info.get('email', ''),
                'basket': json.dumps(basket),
            },
        )

        context.update({
            'session_id': session.id,
            'publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        })
        return context


class PaymentConfirmationView(TemplateView):
    template_name = 'payment_confirmation.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        basket = self.request.session.get('basket', {})
        user_info = self.request.session.get('user_info', {})
        email = user_info.get('email')
        branding = Branding.objects.first()

        # Lock products for stock updates
        products_list = []
        total = Decimal("0.00")

        with transaction.atomic():
            for product_id, quantity in basket.items():
                try:
                    product = Product.objects.select_for_update().get(id=product_id)
                except Product.DoesNotExist:
                    continue

                product_total = product.effective_price * quantity
                products_list.append({
                    'product': product,
                    'quantity': quantity,
                    'total': product_total,
                    'discounted': bool(product.discount_price),
                })
                total += product_total
                product.stock_quantity = max(product.stock_quantity - quantity, 0)
                product.save()

        basket_info = calculate_basket(basket)
        basket_info['products'] = products_list
        basket_info['total'] = total
        basket_info['final_total'] = total + basket_info['delivery_fee']

        # ==========================
        # SEND EMAILS (ONCE ONLY)
        # ==========================
        if email and not self.request.session.get("emails_sent"):

            base_context = {
                "user_info": user_info,
                "cart": basket_info,
                "branding": branding,
            }

            # -----------------
            # Customer email
            # -----------------
            customer_html = render_to_string(
                "order_email.html",
                {
                    **base_context,
                    "is_admin": False,
                }
            )

            send_email_by_context(
                subject="Thank You for Your Order!",
                message="Thank you for your order.",
                recipient_list=[email],
                html_message=customer_html,
            )

            # -----------------
            # Admin email
            # -----------------
            admin_users = get_user_model().objects.filter(
                is_staff=True,
                is_active=True
            ).exclude(email='')

            admin_emails = [u.email for u in admin_users if u.email]

            if admin_emails:
                admin_html = render_to_string(
                    "emails/order_email.html",
                    {
                        **base_context,
                        "is_admin": True,
                    }
                )

                send_email_by_context(
                    subject=f"New Order Received from {user_info.get('full_name', 'Customer')}",
                    message="New order received.",
                    recipient_list=admin_emails,
                    html_message=admin_html,
                )

            self.request.session["emails_sent"] = True
            self.request.session.pop("basket", None)
            self.request.session.pop("user_info", None)


        context.update({
            "cart": basket_info,
            "user_email": email,
        })

        return context
