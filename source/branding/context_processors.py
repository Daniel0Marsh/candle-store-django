from .models import Branding


def branding_context(request):
    return {
        "branding": Branding.objects.first(),
    }
