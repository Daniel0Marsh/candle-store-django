from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import HomePage, PrivacyPolicyPage, TermsOfServicePage


class SingletonAdmin(admin.ModelAdmin):
    """
    Base admin configuration for singleton models.
    Prevents adding multiple instances and redirects to the existing instance.
    """

    def has_add_permission(self, request):
        """
        Restrict adding a new instance if one already exists.
        """
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

    def changelist_view(self, request, extra_context=None):
        """
        Redirects to the existing instance instead of showing a list.
        """
        instance = self.model.objects.first()
        if instance:
            return HttpResponseRedirect(
                reverse(f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change", args=[instance.pk])
            )
        return super().changelist_view(request, extra_context)


@admin.register(HomePage)
class HomePageAdmin(SingletonAdmin):
    pass


@admin.register(PrivacyPolicyPage)
class PrivacyPolicyAdmin(SingletonAdmin):
    pass


@admin.register(TermsOfServicePage)
class TermsOfServiceAdmin(SingletonAdmin):
    pass
