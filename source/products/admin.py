from django.contrib import admin
from django.contrib.admin import DateFieldListFilter
from django.utils.html import format_html
from .models import Product, ProductSettings
from django.http import HttpResponseRedirect
from django.urls import reverse


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


@admin.register(ProductSettings)
class ProductSettingsAdmin(SingletonAdmin):
    list_display = ("delivery_fee", "free_delivery_over", "new_product_days", "updated_at")
    fieldsets = (
        (None, {"fields": ("delivery_fee", "free_delivery_over", "new_product_days")}),
    )

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "product_type",
        "price",
        "effective_price",
        "stock_quantity",
        "featured",
        "best_seller",
        "updated_at",
        "image_tag",
    )

    list_editable = ("featured", "best_seller")

    list_filter = (
        "product_type",
        "featured",
        "best_seller",
        ("created_at", DateFieldListFilter),
    )

    search_fields = (
        "title",
        "description",
        "seo_title",
        "seo_description",
    )

    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Product Details", {
            "fields": (
                "title",
                "slug",
                "product_type",
                "description",
                "price",
                "discount_price",
                "stock_quantity",
            )
        }),
        ("Attributes", {
            "fields": (
                "scent",
                "color",
                "size",
                "featured",
                "best_seller",
            )
        }),
        ("Media", {"fields": ("image",)}),
        ("SEO & Social Metadata", {
            "classes": ("collapse",),
            "fields": (
                "canonical_url",
                "seo_title",
                "seo_description",
                "seo_keywords",
                "seo_robots",
                "og_image",
            ),
            "description": "Advanced SEO controls. Leave blank to use automatic fallbacks.",
        }),
        ("System", {
            "classes": ("collapse",),
            "fields": ("created_at", "updated_at"),
        }),
    )

    def image_tag(self, obj):
        """Display a small thumbnail of the product image in the admin list view."""
        if obj.image:
            return format_html('<img src="{}" style="height:50px;"/>', obj.image.url)
        return "-"
    image_tag.short_description = "Image"
