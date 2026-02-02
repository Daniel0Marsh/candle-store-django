from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from django.utils.text import Truncator
import uuid
import json
from django.utils import timezone


def generate_unique_slug(instance, base=None, max_length=50):
    base_slug = slugify(base) if base else f"product-{uuid.uuid4().hex[:8]}"
    base_slug = base_slug[:max_length]
    slug = base_slug
    counter = 1
    ModelClass = instance.__class__
    while ModelClass.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
        slug = f"{base_slug[:max_length-5]}-{counter}"
        counter += 1
    return slug


class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(stock_quantity__gt=0)

    def discounted(self):
        return self.filter(discount_price__gt=0, discount_price__lt=models.F('price'))

    def new(self, days=None):
        from django.utils import timezone

        if days is None:
            # Get the default from StoreSettingsAdmin
            try:
                settings_instance = StoreSettingsAdmin.objects.first()
                days = settings_instance.new_product_days if settings_instance else 30
            except StoreSettingsAdmin.DoesNotExist:
                days = 30

        threshold = timezone.now() - timezone.timedelta(days=days)
        return self.filter(created_at__gte=threshold).order_by("-created_at")

    def gifts(self):
        return self.filter(product_type=Product.ProductType.GIFT)


class ProductSettings(models.Model):
    delivery_fee = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0.00,
        help_text="Flat delivery fee applied to orders."
    )
    free_delivery_over = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00,
        help_text="Make delivery free if basket total is over this amount. Set to 0 to disable."
    )
    new_product_days = models.PositiveIntegerField(
        default=30,
        help_text="Number of days a product is considered 'new'."
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return "Store Pricing Settings"

    class Meta:
        verbose_name = "Store Pricing Setting"
        verbose_name_plural = "Store Pricing Settings"



class Product(models.Model):

    objects = ProductQuerySet.as_manager()

    class ProductType(models.TextChoices):
        CANDLE = "candle", "Candle"
        WAXMELT = "waxmelt", "Wax Melt"
        GIFT = "gift", "Gift"

    class Color(models.TextChoices):
        WHITE = "white", "White"
        PINK = "pink", "Pink"
        BLUE = "blue", "Blue"
        CREAM = "cream", "Cream"
        AMBER = "amber", "Amber"

    class Scent(models.TextChoices):
        LAVENDER = "lavender", "Lavender"
        VANILLA = "vanilla", "Vanilla"
        CINNAMON = "cinnamon", "Cinnamon"
        ROSE = "rose", "Rose"
        OTHER = "other", "Other"

    class Size(models.TextChoices):
        SMALL = "small", "Small"
        MEDIUM = "medium", "Medium"
        LARGE = "large", "Large"

    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
    )


    canonical_url = models.URLField(
        blank=True,
        default=""
    )


    product_type = models.CharField(
        max_length=20,
        choices=ProductType.choices,
        default=ProductType.CANDLE,
        db_index=True,
    )

    title = models.CharField(
        max_length=255,
        default=""
    )
    description = models.TextField(
        default=""
    )

    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0.00
    )
    discount_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0.00
    )

    stock_quantity = models.PositiveIntegerField(
        default=0
    )

    scent = models.CharField(
        max_length=50,
        choices=Scent.choices,
        default=Scent.OTHER,
    )

    color = models.CharField(
        max_length=50,
        choices=Color.choices,
        default=Color.WHITE,
    )

    size = models.CharField(
        max_length=50,
        choices=Size.choices,
        default=Size.MEDIUM,
    )

    featured = models.BooleanField(
        default=False,
        db_index=True
    )
    best_seller = models.BooleanField(
        default=False,
        db_index=True
    )

    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )


    # --- SEO FIELDS ---
    seo_title = models.CharField(
        max_length=255,
        blank=True
    )

    seo_description = models.CharField(
        max_length=320,
        blank=True
    )

    seo_keywords = models.CharField(
        max_length=255,
        blank=True
    )

    seo_robots = models.CharField(
        max_length=50,
        default="index, follow"
    )

    og_image = models.ImageField(
        upload_to="products/og/",
        blank=True,
        null=True
    )
    # -----------------
    # Meta property for templates
    # -----------------
    @property
    def meta(self):
        site_url = getattr(settings, "SITE_URL", "https://lelseasmelts.com")
        absolute_url = self.canonical_url or f"{site_url}{self.get_absolute_url()}"

        title = self.seo_title or self.title
        description = self.seo_description or Truncator(self.description).chars(155)
        image_url = (f"{site_url}{self.og_image.url}" if self.og_image else
                    f"{site_url}{self.image.url}" if self.image else None)
        availability = "https://schema.org/InStock" if self.stock_quantity > 0 else "https://schema.org/OutOfStock"

        json_ld = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": title,
            "description": description,
            "image": image_url,
            "sku": self.slug,
            "brand": {
                "@type": "Brand",
                "name": "Lelsea’s Melts"
            },
            "offers": {
                "@type": "Offer",
                "url": absolute_url,
                "priceCurrency": "GBP",
                "price": str(self.effective_price),
                "availability": availability,
                "itemCondition": "https://schema.org/NewCondition",
                "seller": {
                    "@type": "Organization",
                    "name": "Lelsea’s Melts"
                }
            },
        }

        base_meta = {
            "title": title,
            "description": description,
            "robots": self.seo_robots,
            "canonical_url": absolute_url,
            "keywords": self.seo_keywords,
            "author": "Lelsea’s Melts",
            "og_title": title,
            "og_description": description,
            "og_type": "product",
            "og_image": image_url,
            "og_image_alt": title,
            "og_locale": "en_GB",
            "site_name": "Lelsea’s Melts",
            "twitter_title": title,
            "twitter_description": description,
            "twitter_image": image_url,
            "twitter_card": "summary_large_image",
            "twitter_site": "@lelseasmelts",
            "twitter_creator": None,
            "json_ld": json.dumps(json_ld),
            "hreflangs": None,
        }
        return base_meta


    # -----------------
    # Slug auto-generation & SEO fallbacks
    # -----------------
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, base=self.title)

        site_url = getattr(settings, "SITE_URL", "https://lelseasmelts.com")

        if not self.canonical_url:
            self.canonical_url = f"{site_url}{self.get_absolute_url()}"

        # --- SEO fallbacks ---
        if not self.seo_title:
            self.seo_title = f"{self.title} | Handmade {self.get_product_type_display()} | Lelsea’s Melts"

        if not self.seo_description:
            self.seo_description = Truncator(
                f"{self.title} – a handmade {self.get_product_type_display().lower()} "
                f"from Lelsea’s Melts. Beautiful home fragrance made in the UK."
            ).chars(155)

        if not self.seo_keywords:
            self.seo_keywords = ", ".join(filter(None, [
                "wax melts" if self.product_type == self.ProductType.WAXMELT else None,
                "scented candles" if self.product_type == self.ProductType.CANDLE else None,
                "handmade candles",
                self.scent,
                "home fragrance",
                "Lelsea’s Melts",
            ]))

        super().save(*args, **kwargs)



    # -----------------
    # Sitemap & URL support
    # -----------------
    def get_absolute_url(self):
        return reverse("product_detail", kwargs={"product_slug": self.slug})


    class Meta:
        indexes = [
            models.Index(fields=['product_type', 'featured']),
            models.Index(fields=['product_type', 'best_seller']),
        ]
        ordering = ['title']

    def __str__(self):
        return f"{self.title} ({self.get_product_type_display()})"

    @property
    def effective_price(self):
        """
        Returns the discounted price if valid, otherwise the base price.
        """
        if self.discount_price and self.discount_price > 0:
            return min(self.discount_price, self.price)
        return self.price

