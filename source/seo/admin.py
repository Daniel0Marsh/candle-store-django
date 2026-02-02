from django.contrib import admin
from .models import PageSEO


@admin.register(PageSEO)
class PageSEOAdmin(admin.ModelAdmin):
    list_display = (
        'url_path',
        'title',
        'robots',
        'has_og_image',
        'has_json_ld',
    )

    list_filter = (
        'url_path',
        'robots',
        'og_type',
        'twitter_card',
    )

    search_fields = (
        'title',
        'description',
        'og_title',
        'og_description',
    )

    ordering = ('url_path',)

    readonly_fields = ()

    fieldsets = (
        ("Page Target", {
            "fields": ("url_path",)
        }),

        ("Core SEO (Google)", {
            "fields": (
                "title",
                "description",
                "canonical_url",
                "robots",
                "language",
            )
        }),

        ("Open Graph (Facebook / LinkedIn)", {
            "fields": (
                "og_title",
                "og_description",
                "og_image",
                "og_type",
                "og_locale",
                "site_name",
            ),
            "classes": ("collapse",),
        }),

        ("Twitter / X", {
            "fields": (
                "twitter_title",
                "twitter_description",
                "twitter_image",
                "twitter_card",
                "twitter_site",
            ),
            "classes": ("collapse",),
        }),

        ("Structured Data", {
            "fields": ("json_ld",),
            "classes": ("collapse",),
        }),
    )

    def has_og_image(self, obj):
        return bool(obj.og_image)

    has_og_image.boolean = True
    has_og_image.short_description = "OG Image"

    def has_json_ld(self, obj):
        return bool(obj.json_ld)

    has_json_ld.boolean = True
    has_json_ld.short_description = "JSON-LD"
