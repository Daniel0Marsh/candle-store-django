from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import (
    HomePage,
    HomePageFeatureSection,
    TermsAndPolicies,
)


class SingletonAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

    def changelist_view(self, request, extra_context=None):
        instance = self.model.objects.first()
        if instance:
            return HttpResponseRedirect(
                reverse(
                    f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change",
                    args=[instance.pk],
                )
            )
        return super().changelist_view(request, extra_context)


class HomePageFeatureSectionInline(admin.TabularInline):
    model = HomePageFeatureSection
    extra = 0
    max_num = 3
    ordering = ("order",)
    fields = (
        "order",
        "image",
        "image_alt_text",
        "title",
        "subheading",
        "cta_text",
        "cta_url",
    )


@admin.register(HomePage)
class HomePageAdmin(SingletonAdmin):
    inlines = [HomePageFeatureSectionInline]


@admin.register(TermsAndPolicies)
class TermsAndPoliciesAdmin(SingletonAdmin):
    """
    Admin for rich-text editable store policies with singleton enforcement.
    """
    readonly_fields = ("updated_at",)
    fieldsets = (
        ("Terms of Service", {"fields": ("terms_of_service",)}),
        ("Privacy Policy", {"fields": ("privacy_policy",)}),
        ("Refund Policy", {"fields": ("refund_policy",)}),
        ("Shipping Policy", {"fields": ("shipping_policy",)}),
        ("Metadata", {"fields": ("updated_at",)}),
    )
    list_display = ("updated_at",)