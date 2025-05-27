from django.views.generic import TemplateView
from branding.models import Branding
from services.models import Service


class Handler400View(TemplateView):
    """
    Custom view to handle HTTP 400 Bad Request errors.

    Renders the '400.html' template and provides branding and services
    context for consistent site layout.
    """
    template_name = '400.html'

    def get_context_data(self, **kwargs):
        """
        Returns context data for the 400 error page.

        Includes the first Branding object and all available Service objects.
        """
        context = {
            "branding": Branding.objects.first(),
            "services": Service.objects.all(),
        }
        return context


class Handler403View(TemplateView):
    """
    Custom view to handle HTTP 403 Forbidden errors.

    Renders the '403.html' template and provides branding and services
    context for consistent site layout.
    """
    template_name = '403.html'

    def get_context_data(self, **kwargs):
        """
        Returns context data for the 403 error page.

        Includes the first Branding object and all available Service objects.
        """
        context = {
            "branding": Branding.objects.first(),
            "services": Service.objects.all(),
        }
        return context


class Error404View(TemplateView):
    """
    Custom view to handle HTTP 404 Not Found errors.

    Renders the '404.html' template and provides branding and services
    context for consistent site layout.
    """
    template_name = '404.html'

    def get_context_data(self, **kwargs):
        """
        Returns context data for the 404 error page.

        Includes the first Branding object and all available Service objects.
        """
        context = {
            "branding": Branding.objects.first(),
            "services": Service.objects.all(),
        }
        return context


class Handler500View(TemplateView):
    """
    Custom view to handle HTTP 500 Internal Server errors.

    Renders the '500.html' template and provides branding and services
    context for consistent site layout.
    """
    template_name = '500.html'

    def get_context_data(self, **kwargs):
        """
        Returns context data for the 500 error page.

        Includes the first Branding object and all available Service objects.
        """
        context = {
            "branding": Branding.objects.first(),
            "services": Service.objects.all(),
        }
        return context
