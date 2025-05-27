from django.views.generic import TemplateView
from django.core.mail import send_mail
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from itertools import chain

from .models import HomePage, PrivacyPolicyPage, TermsOfServicePage
from branding.models import Branding
from products.models import Candle, WaxMelt, StorePricingSettings

import urllib.parse
import urllib.request
import json


class HomePageView(TemplateView):
    """
    Renders the home page with featured and best-selling products,
    branding, homepage content, cart item count, and pricing settings.
    """
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch featured and best-selling products
        featured_candles = Candle.objects.filter(featured=True)
        featured_waxmelts = WaxMelt.objects.filter(featured=True)
        best_candles = Candle.objects.filter(best_seller=True)
        best_waxmelts = WaxMelt.objects.filter(best_seller=True)

        # Combine and annotate products
        featured_products = list(featured_candles) + list(featured_waxmelts)
        best_sellers = list(chain(best_candles, best_waxmelts))[:8]

        for product in featured_products + best_sellers:
            product.product_type = 'candle' if isinstance(product, Candle) else 'waxmelt'

        # Retrieve session cart item count
        basket = self.request.session.get('basket', {})
        item_count = sum(basket.values())

        # Populate template context
        context.update({
            "branding": Branding.objects.first(),
            "home": HomePage.objects.first(),
            "featured_products": featured_products,
            "best_sellers": best_sellers,
            "cart": {'item_count': item_count},
            "pricing_settings": StorePricingSettings.objects.first(),
        })

        return context

    @staticmethod
    def post(request):
        """
        Handles contact form submission with Google reCAPTCHA verification.
        Sends confirmation emails to admins and all registered users.
        """
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        if not (name and email and message):
            messages.error(request, "Please fill in all the fields.")
            return render(request, 'contact_us.html')

        recaptcha_response = request.POST.get('g-recaptcha-response')
        if not recaptcha_response:
            messages.error(request, "Please complete the CAPTCHA before submitting your message.")
            return render(request, 'contact_us.html')

        # Validate CAPTCHA
        data = urllib.parse.urlencode({
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }).encode()
        req = urllib.request.Request('https://www.google.com/recaptcha/api/siteverify', data=data)
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode())

        if result.get('success'):
            subject = f"Codeblock Contact Us Message from {name}"
            content = f"Sender's Name: {name}\nSender's Email: {email}\nMessage:\n{message}"

            def send_email(recipient):
                send_mail(subject, content, email, [recipient], fail_silently=False)

            # Send to admin
            send_email(settings.DEFAULT_FROM_EMAIL)

            # Send to all users
            for user in User.objects.exclude(email="").iterator():
                send_email(user.email)

            messages.success(request, "Your message has been sent successfully!")
            return render(request, 'contact.html')
        else:
            messages.error(request, "There was an issue with the CAPTCHA. Please try again.")
            return render(request, 'contact.html')


class ProductSearchView(TemplateView):
    """
    Displays search results for candles and wax melts based on a query string.
    """
    template_name = 'search_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')

        context.update({
            'query': query,
            'candles': Candle.objects.filter(Q(title__icontains=query)) if query else Candle.objects.none(),
            'waxmelts': WaxMelt.objects.filter(Q(title__icontains=query)) if query else WaxMelt.objects.none(),
            'cart': {'item_count': sum(self.request.session.get('basket', {}).values())},
            'branding': Branding.objects.first(),
            'home': HomePage.objects.first(),
        })

        return context


class AboutPageView(TemplateView):
    """
    Renders the 'About Us' page.
    """
    template_name = 'about_us.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "cart": {'item_count': sum(self.request.session.get('basket', {}).values())},
            "branding": Branding.objects.first(),
            "home": HomePage.objects.first(),
        })
        return context


class PrivacyPolicyPageView(TemplateView):
    """
    Renders the Privacy Policy page.
    """
    template_name = 'privacy_policy.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "cart": {'item_count': sum(self.request.session.get('basket', {}).values())},
            "branding": Branding.objects.first(),
            "privacy_policy": PrivacyPolicyPage.objects.first(),
        })
        return context


class TermsOfServicePageView(TemplateView):
    """
    Renders the Terms of Service page.
    """
    template_name = 'terms_of_service.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "cart": {'item_count': sum(self.request.session.get('basket', {}).values())},
            "branding": Branding.objects.first(),
            "terms_of_service": TermsOfServicePage.objects.first(),
        })
        return context
