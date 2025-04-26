from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from branding.models import Branding
from products.models import Candle, WaxMelt, StorePricingSettings
from decimal import Decimal
from django.conf import settings
import stripe
import json
from django.db import transaction
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth import get_user_model

# Set Stripe secret key
stripe.api_key = settings.STRIPE_SECRET_KEY


class BasketPageView(TemplateView):
    template_name = 'basket.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        basket = self.request.session.get('basket', {})

        products = []
        total = Decimal("0.00")
        for product_id, quantity in basket.items():
            try:
                product = Candle.objects.get(id=product_id)
            except Candle.DoesNotExist:
                try:
                    product = WaxMelt.objects.get(id=product_id)
                except WaxMelt.DoesNotExist:
                    continue
            price = product.discount_price if product.discount_price else product.price
            product_total = price * quantity
            products.append({
                'product': product,
                'quantity': quantity,
                'total': product_total,
                'discounted': product.discount_price is not None
            })
            total += product_total

        pricing_settings = StorePricingSettings.objects.first()
        delivery_fee = Decimal("0.00")

        if pricing_settings:
            if not pricing_settings.free_delivery_over or total < pricing_settings.free_delivery_over:
                delivery_fee = pricing_settings.delivery_fee

        context.update({
            "cart": {
                'item_count': sum(basket.values()),
                'products': products,
                'total': total,
                'final_total': total + delivery_fee,
                'delivery_fee': delivery_fee,
                'free_delivery_applied': pricing_settings.free_delivery_over and total >= pricing_settings.free_delivery_over
            },
            "pricing_settings": pricing_settings,
            "branding": Branding.objects.first(),
        })
        return context

    def post(self, request, *args, **kwargs):
        """
        Handle adding/removing items or updating quantities in the basket.
        """
        action = request.POST.get('action')
        product_id = request.POST.get('product_id')
        basket = request.session.get('basket', {})

        if action == 'remove':
            basket.pop(product_id, None)
        elif action == 'update':
            new_quantity = int(request.POST.get('quantity', 1))
            if new_quantity <= 0:
                basket.pop(product_id, None)
            else:
                basket[product_id] = new_quantity

        request.session['basket'] = basket
        return redirect('basket')


class UserDetailsPageView(TemplateView):
    template_name = 'user_details.html'

    def get_context_data(self, **kwargs):
        """
        Get context data for the template.
        """

        # Get the current shopping basket from the session
        basket = self.request.session.get('basket', {})

        # Calculate the total item count in the basket
        item_count = sum(basket.values())

        context = {
            "cart": {'item_count': item_count},
            "branding": Branding.objects.first(),
        }
        return context

    def post(self, request, *args, **kwargs):
        """
        Handle form submission for user details and proceed to Stripe payment.
        """
        user_info = {
            'full_name': request.POST.get('full_name'),
            'email': request.POST.get('email'),
            'address_line1': request.POST.get('address_line1'),
            'address_line2': request.POST.get('address_line2', ''),
            'city': request.POST.get('city'),
            'postal_code': request.POST.get('postal_code'),
            'country': request.POST.get('country')
        }

        # Save user info into session for later use
        request.session['user_info'] = user_info

        # Redirect to Stripe payment page
        return redirect('stripe_payment')


class StripePaymentView(TemplateView):
    template_name = 'stripe_payment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Retrieve user and basket information from session
        user_info = self.request.session.get('user_info', {})
        basket = self.request.session.get('basket', {})

        line_items = []
        total = Decimal("0.00")

        # Build product line items
        for product_id, quantity in basket.items():
            try:
                product = Candle.objects.get(id=product_id)
            except Candle.DoesNotExist:
                try:
                    product = WaxMelt.objects.get(id=product_id)
                except WaxMelt.DoesNotExist:
                    continue

            price = product.discount_price if product.discount_price else product.price
            total += price * quantity

            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': int(price * 100),
                    'product_data': {
                        'name': product.title,
                    },
                },
                'quantity': quantity,
            })

        # Add delivery fee if applicable
        delivery_fee = Decimal("0.00")
        pricing_settings = StorePricingSettings.objects.first()
        if pricing_settings:
            if not pricing_settings.free_delivery_over or total < pricing_settings.free_delivery_over:
                delivery_fee = pricing_settings.delivery_fee
                total += delivery_fee

                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(delivery_fee * 100),
                        'product_data': {
                            'name': "Delivery Fee",
                        },
                    },
                    'quantity': 1,
                })

        # Create Stripe Checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url='http://localhost:8000/success/',
            cancel_url='http://localhost:8000/basket/',
            metadata={
                'email': user_info.get('email', ''),
                'basket': json.dumps(basket),
            }
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

        products = []
        total = Decimal("0.00")

        # Wrap updates inside a transaction
        with transaction.atomic():
            for product_id, quantity in basket.items():
                product = None
                try:
                    product = Candle.objects.select_for_update().get(id=product_id)
                except Candle.DoesNotExist:
                    try:
                        product = WaxMelt.objects.select_for_update().get(id=product_id)
                    except WaxMelt.DoesNotExist:
                        continue

                price = product.discount_price if product.discount_price else product.price
                product_total = price * quantity
                products.append({
                    'product': product,
                    'quantity': quantity,
                    'total': product_total,
                    'discounted': product.discount_price is not None,
                })
                total += product_total

                # Reduce stock quantity
                if product.stock_quantity >= quantity:
                    product.stock_quantity -= quantity
                else:
                    product.stock_quantity = 0  # avoid negative stock just in case
                product.save()

        pricing_settings = StorePricingSettings.objects.first()
        delivery_fee = Decimal("0.00")
        if pricing_settings:
            if not pricing_settings.free_delivery_over or total < pricing_settings.free_delivery_over:
                delivery_fee = pricing_settings.delivery_fee

        cart_info = {
            'item_count': sum(basket.values()),
            'products': products,
            'total': total,
            'final_total': total + delivery_fee,
            'delivery_fee': delivery_fee,
            'free_delivery_applied': pricing_settings and pricing_settings.free_delivery_over and total >= pricing_settings.free_delivery_over
        }

        branding = Branding.objects.first()

        # Send confirmation email to customer
        if email:
            subject = "Thank You for Your Order!"

            html_content = render_to_string('confirmation_email.html', {
                'user_info': user_info,
                'cart': cart_info,
                'branding': branding,
            })
            text_content = strip_tags(html_content)

            email_message = EmailMultiAlternatives(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [email],
            )
            email_message.attach_alternative(html_content, "text/html")
            email_message.send()

        # Send notification email to admin(s)
        admin_users = get_user_model().objects.filter(is_staff=True, is_active=True).exclude(email='')
        admin_emails = [admin.email for admin in admin_users if admin.email]

        if admin_emails:
            admin_subject = f"New Order Received from {user_info.get('first_name', 'Customer')} {user_info.get('last_name', '')}"

            admin_html_content = render_to_string('admin_order_notification_email.html', {
                'user_info': user_info,
                'cart': cart_info,
                'branding': branding,
            })
            admin_text_content = strip_tags(admin_html_content)

            admin_email_message = EmailMultiAlternatives(
                admin_subject,
                admin_text_content,
                settings.DEFAULT_FROM_EMAIL,
                admin_emails,
            )
            admin_email_message.attach_alternative(admin_html_content, "text/html")
            admin_email_message.send()

        # Clear basket and session info
        self.request.session.pop('basket', None)
        self.request.session.pop('user_info', None)

        context.update({
            "cart": cart_info,
            "pricing_settings": pricing_settings,
            "branding": branding,
            "user_email": email,
        })
        return context
