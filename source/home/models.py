from django.db import models
from django_ckeditor_5.fields import CKEditor5Field


class HomePage(models.Model):
    """
    Model representing the homepage information for the website.
    This model stores essential details such as the site's branding elements,
    contact information, and media assets used on the homepage.
    """

    DEFAULT_IMAGE = "default/placeholder.png"
    DEFAULT_VIDEO = "default/placeholder.mp4"

    hero_image = models.ImageField(
        upload_to="home_page/",
        help_text="Upload the hero section background image.",
        default=DEFAULT_IMAGE
    )
    about_image = models.ImageField(
        upload_to="home_page/",
        help_text="Upload the about section image.",
        default=DEFAULT_IMAGE
    )

    hero_title = models.CharField(
        max_length=100,
        help_text="Main title for the hero section.",
        default="HANDCRAFTED WAX MELTS & CANDLES"
    )
    hero_subheading = models.CharField(
        max_length=255,
        help_text="Subheading text for the hero section.",
        default="A peaceful, luxury stay designed for ultimate relaxation, fun, and pampering."
    )
    about_title = models.CharField(
        max_length=100,
        help_text="Title for the about section.",
        default="ABOUT US"
    )
    about_subheading = models.CharField(
        max_length=255,
        help_text="Subheading for the about section.",
        default="We take pride in producing high-quality hand-pourd wax melts and candles made from natural ingredients. Our scents are curated to create inviting and relaxing atmospheres in your home."
    )

    about_us_page_content = CKEditor5Field(config_name='default', null=True, blank=True,
                             help_text="This is the contents of the about us page.",)

    def __str__(self):
        return "Home Page Content"

    class Meta:
        verbose_name = "Home Page Content"
        verbose_name_plural = "Home Page Content"


class PrivacyPolicyPage(models.Model):
    """
    Model representing the privacy policy.
    """

    content = CKEditor5Field(config_name='default', null=True, blank=True)

    def __str__(self):
        return "Privacy Policy Content"

    class Meta:
        verbose_name = "Privacy Policy Content"
        verbose_name_plural = "Privacy Policy Content"


class TermsOfServicePage(models.Model):
    """
    Model representing the terms of service.
    """

    content = CKEditor5Field(config_name='default', null=True, blank=True)

    def __str__(self):
        return "Terms Of Service Page Content"

    class Meta:
        verbose_name = "Terms Of Service Page Content"
        verbose_name_plural = "Terms Of Service Page Content"
