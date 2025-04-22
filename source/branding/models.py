from django.db import models


class Branding(models.Model):
    """
    Model representing the Branding information for the website.

    This model stores essential details such as the company’s branding elements,
    contact information, meta tags, and media assets.
    """

    company_name = models.CharField(max_length=255, default="Your Company Name",
                                    help_text="Enter the full name of the company.")
    company_email = models.EmailField(default="contact@company.com",
                                      help_text="Enter the official company email address.")
    company_phone = models.CharField(max_length=20, default="+1-555-000-0000",
                                     help_text="Enter the company’s contact number (e.g., +1-555-000-0000).")
    company_address = models.TextField(default="123 Street Name, City, Country, ZIP",
                                       help_text="Enter the full address of the company, including city and ZIP code.")

    logo = models.ImageField(upload_to="branding/", default="default/default_logo.png",
                             help_text="Upload the website logo.")
    favicon = models.ImageField(upload_to="branding/", default="default/default_icon.ico",
                                help_text="Upload the favicon (ICO or PNG).")

    footer_video = models.FileField(upload_to="branding/videos/", help_text="Upload the website footer video",
                                    default="default/footer_video.mp4")

    meta_keywords = models.CharField(max_length=255, blank=True,
                                     default="generic, branding, business, website, company",
                                     help_text="Enter meta keywords for SEO (comma-separated).")
    meta_description = models.TextField(blank=True, default="Enter a meta description for SEO.",
                                        help_text="Enter a meta description for SEO.")

    tiktok_link = models.URLField(blank=True, default="https://tiktok.com/yourcompany",
                                   help_text="Link to your TikTok profile.")
    facebook_link = models.URLField(blank=True, default="https://facebook.com/yourcompany",
                                    help_text="Link to your Facebook page.")
    instagram_link = models.URLField(blank=True, default="https://instagram.com/yourcompany",
                                     help_text="Link to your Instagram profile.")

    def __str__(self):
        return "Branding Info"
