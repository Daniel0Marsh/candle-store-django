from django.views.generic import TemplateView
from django.core.mail import send_mail
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.models import User
from itertools import chain
from .models import HomePage, PrivacyPolicyPage, TermsOfServicePage
from branding.models import Branding
from products.models import Candle, WaxMelt, StorePricingSettings
from django.db.models import Q
import requests
import json
import urllib
import urllib.parse
import urllib.request


class HomePageView(TemplateView):
    """
    View for rendering the home page.

    Attributes:
        template_name (str): Name of the template file to be used.
    """
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        """
        Get the context data for rendering the template.

        Returns:
            dict: Context data for the template.
        """
        # Get featured products
        featured_candles = Candle.objects.filter(featured=True)
        featured_waxmelts = WaxMelt.objects.filter(featured=True)
        featured_products = list(featured_candles) + list(featured_waxmelts)

        # Get best sellers
        best_selling_candles = Candle.objects.filter(best_seller=True)
        best_selling_waxmelts = WaxMelt.objects.filter(best_seller=True)
        combined_best_sellers = list(chain(best_selling_candles, best_selling_waxmelts))[:8]

        # Add product type dynamically for easy reference in the template
        for product in featured_products:
            if isinstance(product, Candle):
                product.product_type = 'candle'
            elif isinstance(product, WaxMelt):
                product.product_type = 'waxmelt'

        for product in combined_best_sellers:
            if isinstance(product, Candle):
                product.product_type = 'candle'
            elif isinstance(product, WaxMelt):
                product.product_type = 'waxmelt'

        # Get the current shopping basket from the session
        basket = self.request.session.get('basket', {})

        # Calculate the total item count in the basket
        item_count = sum(basket.values())

        context = {
            "branding": Branding.objects.first(),
            "home": HomePage.objects.first(),
            "featured_products": featured_products,
            "best_sellers": combined_best_sellers,
            "cart": {'item_count': item_count},
            "pricing_settings": StorePricingSettings.objects.first()
        }

        return context

    @staticmethod
    def post(request):
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        if email and message and name:
            # Check if the reCAPTCHA response is present
            recaptcha_response = request.POST.get('g-recaptcha-response')
            if not recaptcha_response:
                messages.error(request, "Please complete the CAPTCHA before submitting your message.")
                return render(request, 'contact_us.html')  # Return the page with error message

            # Begin reCAPTCHA validation
            url = 'https://www.google.com/recaptcha/api/siteverify'
            values = {
                'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            data = urllib.parse.urlencode(values).encode()
            req = urllib.request.Request(url, data=data)
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())
            # End reCAPTCHA validation

            if result['success']:
                # Send the email if CAPTCHA is valid
                subject = f"Codeblock Contact Us Message from {name}"
                message_content = f"Sender's Name: {name}\nSender's email: {email}\nSender's message: {message}"

                def send_email(recipient_email):
                    send_mail(
                        subject=subject,
                        message=message_content,
                        from_email=email,
                        recipient_list=[recipient_email],
                        fail_silently=False,
                    )

                # Send email to the main contact email
                send_email(settings.DEFAULT_FROM_EMAIL)

                # Send email to all registered users
                users = User.objects.all()
                for user in users:
                    if user.email:
                        send_email(user.email)

                messages.success(request, "Your message has been sent successfully!")
                return render(request, 'contact.html')

            # If CAPTCHA failed or data is missing, show an error
            messages.error(request, "There was an issue sending your message. Please try again.")
            return render(request, 'contact.html')

        else:
            # If required fields are missing
            messages.error(request, "Please fill in all the fields.")
            return render(request, 'contact_us.html')


class ProductSearchView(TemplateView):
    template_name = 'search_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')

        # Add search results
        context['query'] = query
        context['candles'] = Candle.objects.filter(Q(title__icontains=query)) if query else Candle.objects.none()
        context['waxmelts'] = WaxMelt.objects.filter(Q(title__icontains=query)) if query else WaxMelt.objects.none()

        # Add global context (cart, branding, homepage)
        basket = self.request.session.get('basket', {})
        item_count = sum(basket.values())
        context['cart'] = {'item_count': item_count}
        context['branding'] = Branding.objects.first()
        context['home'] = HomePage.objects.first()

        return context


class AboutPageView(TemplateView):
    """
    View for displaying the about page.
    """
    template_name = 'about_us.html'

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
            "home": HomePage.objects.first(),
        }
        return context


class PrivacyPolicyPageView(TemplateView):
    """
    View for displaying privacy policy.
    """
    template_name = 'privacy_policy.html'

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
            'privacy_policy': PrivacyPolicyPage.objects.first(),
        }
        return context


class TermsOfServicePageView(TemplateView):
    """
    View for displaying terms of service.
    """
    template_name = 'terms_of_service.html'

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
            'terms_of_service': TermsOfServicePage.objects.first(),
        }
        return context
