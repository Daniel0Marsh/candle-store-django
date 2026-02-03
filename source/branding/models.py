from django.db import models

class Branding(models.Model):
    """
    Model representing the Branding information for the website.

    Stores company branding, contact info, media assets, working hours,
    SEO fields, and social media links for structured data.
    """

    company_name = models.CharField(
        max_length=255,
        help_text="Full company name",
        default="Lelsea’s Melts"
    )

    company_email = models.EmailField(
        help_text="Official company email",
        default="info@lelseasmelts.com"
    )

    company_phone = models.CharField(
        max_length=20,
        help_text="Company contact number",
        default="+44 1234 567890"
    )

    company_address = models.CharField(
        max_length=255,
        help_text="Full address, including city and ZIP",
        default="Kent, United Kingdom"
    )

    working_hours = models.CharField(
        max_length=255,
        help_text="Working hours (for local SEO)",
        default="Monday – Friday: 9am – 5pm"
    )

    top_bar = models.CharField(
        max_length=255,
        help_text="Top bar text",
        default="Hand-poured wax melts & candles • Free UK delivery on orders over"
    )

    hero_image = models.ImageField(
        upload_to="home_page/",
        help_text="Upload the hero section background image.",
        default="default/placeholder.jpg"
    )

    hero_image_alt_text = models.CharField(
        max_length=255,
        help_text="Alternative text for the hero image.",
        default="Luxury handmade wax melts and scented candles by Lelsea’s Melts"
    )

    footer_video = models.FileField(
        upload_to="branding/videos/",
        help_text="Upload the website footer video",
        default="default/footer-video.mp4"
    )

    # Logos
    logo = models.ImageField(
        upload_to="branding/",
        default="default/White-Logo.webp"
    )

    logo_alt_text = models.CharField(
        max_length=255,
        default="Lelsea’s Melts logo – Handmade wax melts and scented candles"
    )

    logo_geo_tag = models.CharField(
        max_length=255,
        blank=True,
        default="51.2787,1.0810"  # Kent, UK
    )

    logo_dark = models.ImageField(
        upload_to="branding/",
        default="default/Gold-Logo.webp"
    )

    logo_dark_alt_text = models.CharField(
        max_length=255,
        default="Lelsea’s Melts dark logo – Luxury home fragrance brand"
    )

    favicon = models.ImageField(
        upload_to="branding/",
        default="default/favicon.ico"
    )

    # SEO
    site_map_description = models.TextField(
        blank=True,
        default=(
            "Lelsea’s Melts is a UK-based home fragrance brand specialising in handmade "
            "wax melts and scented candles. Our products are hand-poured using high-quality "
            "waxes and long-lasting fragrances to fill your home with beautiful scents."
        )
    )

    meta_keywords = models.CharField(
        max_length=512,
        blank=True,
        default=(
            "wax melts, scented candles, handmade candles, luxury wax melts, "
            "soy wax candles, home fragrance, candle shop UK, wax melt shop, "
            "Lelsea’s Melts"
        )
    )

    # Social media links (for structured data / JSON-LD)
    facebook_url = models.URLField(
        blank=True,
        default="https://www.facebook.com/lelseasmelts"
    )

    instagram_url = models.URLField(
        blank=True,
        default="https://www.instagram.com/lelseasmelts"
    )

    twitter_url = models.URLField(
        blank=True,
        default=""
    )

    linkedin_url = models.URLField(
        blank=True,
        default=""
    )

    def social_links(self):
        """Return all non-empty social links as a list for JSON-LD"""
        return [url for url in [
            self.facebook_url,
            self.instagram_url,
            self.twitter_url,
            self.linkedin_url
        ] if url]

    def __str__(self):
        return "Branding Info"

    class Meta:
        verbose_name = "Branding"
        verbose_name_plural = "Branding"
