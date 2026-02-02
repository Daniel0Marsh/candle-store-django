from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Branding


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
                reverse(
                    f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change",
                    args=[instance.pk]
                )
            )
        return super().changelist_view(request, extra_context)


@admin.register(Branding)
class BrandingAdmin(SingletonAdmin):
    """
    Admin configuration for Branding model.
    Organizes fields for easier editing and SEO management.
    """

    fieldsets = (
        ("Company Information", {
            "fields": ("company_name", "company_email", "company_phone", "company_address", "working_hours", "top_bar", "hero_image", "footer_video")
        }),
        ("Social Media", {
            "fields": ("facebook_url", "twitter_url", "linkedin_url", "instagram_url")
        }),
        ("Logos", {
            "fields": (
                ("logo", "logo_alt_text", "logo_geo_tag"),
                ("logo_dark", "logo_dark_alt_text"),
                "favicon",
            )
        }),
        ("SEO / Sitemap", {
            "fields": ("site_map_description",)
        }),
    )

    readonly_fields = ()
    list_display = ("company_name", "company_email", "company_phone")
