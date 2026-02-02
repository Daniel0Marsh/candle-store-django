from django.db import models
from django.conf import settings
import json


def default_json_ld():
    data = {
        "@context": "https://schema.org",
        "@type": "Store",
        "name": "Lelsea’s Melts",
        "url": "https://lelseasmelts.com",
        "description": (
            "Lelsea’s Melts is a UK-based home fragrance store specialising in "
            "handmade wax melts and scented candles."
        ),
        "address": {
            "@type": "PostalAddress",
            "addressCountry": "GB"
        }
    }
    return json.dumps(data, ensure_ascii=False)



class PageSEO(models.Model):
    STATIC_PAGE_CHOICES = [
        ('/', 'Home'),
        ('/products/', 'All Products'),
        ('/products/new/', 'New Arrivals'),
        ('/products/candles/', 'Candles'),
        ('/products/waxmelts/', 'Wax Melts'),
        ('/products/gifts/', 'Gift Sets'),
        ('/products/offers/', 'Offers'),
        ('/basket/', 'Basket'),
        ('/checkout/details/', 'Checkout Details'),
        ('/checkout/payment/', 'Payment'),
        ('/search/', 'Search'),
        ('/contact/', 'Contact'),
        ('/checkout/success/', 'Checkout Success'),
        ('/privacy-policy/', 'Privacy Policy'),
        ('/terms-of-service/', 'Terms of Service'),
        ('/refund-policy/', 'Refund Policy'),
        ('/shipping-policy/', 'Shipping Policy'),
    ]

    url_path = models.CharField(
        max_length=255,
        choices=STATIC_PAGE_CHOICES,
        unique=True,
        db_index=True,
        help_text="Select the static page this SEO entry applies to"
    )

    # ======================
    # Core SEO
    # ======================
    title = models.CharField(
        max_length=60,
        default="Lelsea’s Melts | Handmade Wax Melts & Scented Candles",
        help_text="Max 60 characters recommended for Google SERP"
    )
    description = models.TextField(
        max_length=160,
        default=(
            "Shop handmade wax melts and scented candles from Lelsea’s Melts. "
            "Luxury home fragrance, hand-poured in the UK."
        ),
        help_text="Max 155–160 characters recommended"
    )
    canonical_url = models.URLField(
        blank=True,
        null=True,
        default="",
        help_text="Absolute canonical URL. Leave blank to auto-generate."
    )
    robots = models.CharField(
        max_length=100,
        default="index, follow, max-snippet:-1, max-image-preview:large",
        help_text="Default is safe for Google indexing"
    )
    language = models.CharField(
        max_length=10,
        default="en-GB",
        help_text="HTML lang attribute (e.g. en-GB, en-US)"
    )
    keywords = models.CharField(max_length=255, blank=True, null=True)

    # ======================
    # Open Graph
    # ======================
    og_title = models.CharField(
        max_length=255,
        default="Lelsea’s Melts | Handmade Wax Melts & Candles",
        help_text="Falls back to Title if empty"
    )

    og_description = models.TextField(
        default=(
            "Discover luxury wax melts and scented candles, handmade in the UK by "
            "Lelsea’s Melts."
        ),
        help_text="Falls back to Description if empty"
    )
    og_image = models.ImageField(
        upload_to='seo/',
        default="default/hero_image.webp",
        help_text="1200x630 recommended"
    )
    og_image_alt = models.CharField(max_length=255, blank=True, null=True)
    og_image_width = models.PositiveIntegerField(blank=True, null=True)
    og_image_height = models.PositiveIntegerField(blank=True, null=True)
    og_type = models.CharField(max_length=50, default="website")
    og_locale = models.CharField(max_length=20, default="en_GB")
    site_name = models.CharField(max_length=255, default="Lelsea’s Melts")

    # ======================
    # Twitter Cards
    # ======================
    twitter_title = models.CharField(
        max_length=255,
        default="Lelsea’s Melts | Handmade Wax Melts & Candles",
        help_text="Falls back to OG Title"
    )

    twitter_description = models.TextField(
        default=(
            "Luxury handmade wax melts and scented candles from Lelsea’s Melts."
        ),
        help_text="Falls back to OG Description"
    )
    twitter_image = models.ImageField(
        upload_to='seo/',
        default="default/hero_image.webp",
        help_text="1200x630 recommended"
    )


    twitter_image_alt = models.CharField(max_length=255, blank=True, null=True)
    twitter_card = models.CharField(max_length=50, default="summary_large_image")
    twitter_site = models.CharField(max_length=255, default="@lelseasmelts")
    twitter_creator = models.CharField(max_length=255, blank=True, null=True)

    # ======================
    # Structured Data
    # ======================
    json_ld = models.TextField(
        blank=True,
        null=True,
        default=default_json_ld,
        help_text="Optional JSON-LD schema (Organization, WebPage, Service, etc.)"
    )

    # -----------------
    # Meta property for templates
    # -----------------
    @property
    def meta(self):
        site_url = getattr(settings, "SITE_URL", "https://lelseasmelts.com")
        canonical = self.canonical_url or f"{site_url}{self.url_path}"

        # OG image absolute URL
        og_image_url = f"{site_url}{self.og_image.url}" if self.og_image else f"{site_url}{settings.MEDIA_URL}default/hero_image.webp"

        # Twitter image absolute URL
        twitter_image_url = f"{site_url}{self.twitter_image.url}" if self.twitter_image else og_image_url

        return {
            "title": self.title,
            "description": self.description,
            "robots": self.robots,
            "canonical_url": canonical,
            "keywords": self.keywords,
            "og_title": self.og_title or self.title,
            "og_description": self.og_description or self.description,
            "og_type": self.og_type,
            "og_image": og_image_url,
            "og_image_alt": self.og_image_alt,
            "og_image_width": self.og_image_width,
            "og_image_height": self.og_image_height,
            "og_locale": self.og_locale,
            "site_name": self.site_name,
            "twitter_title": self.twitter_title or self.og_title or self.title,
            "twitter_description": self.twitter_description or self.og_description or self.description,
            "twitter_image": twitter_image_url,
            "twitter_image_alt": self.twitter_image_alt or self.og_image_alt,
            "twitter_card": self.twitter_card,
            "twitter_site": self.twitter_site,
            "twitter_creator": self.twitter_creator,
            "json_ld": self.json_ld,
        }

    # -----------------
    # Auto-fill canonical URL
    # -----------------
    def save(self, *args, **kwargs):
        site_url = getattr(settings, "SITE_URL", "https://lelseasmelts.com")
        if not self.canonical_url:
            self.canonical_url = f"{site_url}{self.url_path}"
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Page SEO"
        verbose_name_plural = "Page SEO Entries"
        ordering = ["url_path"]

    def __str__(self):
        return f"{self.get_url_path_display()} SEO"
