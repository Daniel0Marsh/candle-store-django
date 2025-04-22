from django.views.generic import TemplateView
from .models import ErrorPage
from branding.models import Branding
from services.models import Service


class Handler400View(TemplateView):
    template_name = '400.html'

    def get_context_data(self, **kwargs):
        context = {
            "branding": Branding.objects.first(),
            "services": Service.objects.all(),
            "error_video": ErrorPage.objects.filter(error_code='400').first(),
        }
        return context


class Handler403View(TemplateView):
    template_name = '403.html'

    def get_context_data(self, **kwargs):
        context = {
            "branding": Branding.objects.first(),
            "services": Service.objects.all(),
            "error_video": ErrorPage.objects.filter(error_code='403').first(),
        }
        return context


class Error404View(TemplateView):
    template_name = '404.html'

    def get_context_data(self, **kwargs):
        context = {
            "branding": Branding.objects.first(),
            "services": Service.objects.all(),
            "error_video": ErrorPage.objects.filter(error_code='404').first(),
        }
        return context


class Handler500View(TemplateView):
    template_name = '500.html'

    def get_context_data(self, **kwargs):
        context = {
            "branding": Branding.objects.first(),
            "services": Service.objects.all(),
            "error_video": ErrorPage.objects.filter(error_code='500').first(),
        }
        return context
