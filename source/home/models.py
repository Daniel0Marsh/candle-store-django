from django.db import models
from django_ckeditor_5.fields import CKEditor5Field


class HomePage(models.Model):
    """
    Singleton model representing homepage-wide content.
    """

    hero_image = models.ImageField(
        upload_to="home_page/",
        help_text="Upload the hero section background image.",
        default="default/placeholder.jpg"
    )

    hero_title = models.CharField(
        max_length=100,
        help_text="Main title for the hero section.",
        default="Handmade Wax Melts & Scented Candles"
    )

    hero_subheading = models.CharField(
        max_length=255,
        help_text="Subheading text for the hero section.",
        default=(
            "Luxury home fragrance hand-poured in the UK using high-quality waxes "
            "and long-lasting scents."
        )
    )

    hero_image_alt_text = models.CharField(
        max_length=255,
        help_text="Alternative text for the hero image.",
        default=(
            "Handmade wax melts and scented candles by Lelsea’s Melts, "
            "designed to fill your home with beautiful fragrance"
        )
    )

    def __str__(self):
        return "Home Page Content"

    class Meta:
        verbose_name = "Home Page Content"
        verbose_name_plural = "Home Page Content"



class HomePageFeatureSection(models.Model):
    """
    Represents a left-image / right-content section on the homepage.
    """

    home_page = models.ForeignKey(
        HomePage,
        on_delete=models.CASCADE,
        related_name="feature_sections"
    )

    image = models.ImageField(
        upload_to="home_page/features/",
        help_text="Full-height image for this section.",
        default="default/placeholder.jpg"
    )

    image_alt_text = models.CharField(
        max_length=255,
        help_text="Alternative text for the feature image.",
        default=(
            "Handmade wax melts and scented candles by Lelsea’s Melts, "
            "designed to fill your home with beautiful fragrance"
        )
    )

    title = models.CharField(
        max_length=120,
        help_text="SEO-friendly section heading (e.g. Wax Melts, Candles, Handmade)."
    )

    subheading = models.TextField(
        max_length=300,
        help_text="Supporting text describing products or brand values."
    )

    cta_text = models.CharField(
        max_length=50,
        default="Shop now",
        help_text="Button label."
    )

    cta_url = models.CharField(
        max_length=255,
        help_text="Button link URL.",
        default="/products/",
    )

    order = models.PositiveSmallIntegerField(
        default=0,
        help_text="Display order (lower numbers appear first)."
    )

    class Meta:
        ordering = ["order"]
        verbose_name = "Homepage Feature Section"
        verbose_name_plural = "Homepage Feature Sections"

    def __str__(self):
        return self.title



class TermsAndPolicies(models.Model):
    terms_of_service = CKEditor5Field(config_name='default', null=True, blank=True)
    privacy_policy = CKEditor5Field(config_name='default', null=True, blank=True)
    refund_policy = CKEditor5Field(config_name='default', null=True, blank=True)
    shipping_policy = CKEditor5Field(config_name='default', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Store Policies"

