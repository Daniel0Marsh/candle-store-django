from django.db import models


class StorePricingSettings(models.Model):
    delivery_fee = models.DecimalField(
        max_digits=6, decimal_places=2, default=0.00,
        help_text="Flat delivery fee applied to orders."
    )
    free_delivery_over = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        help_text="Make delivery free if basket total is over this amount. Leave blank to disable."
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Store Pricing Settings"

    class Meta:
        verbose_name = "Store Pricing Setting"
        verbose_name_plural = "Store Pricing Settings"


class Candle(models.Model):
    COLOR_CHOICES = [
        ('white', 'White'),
        ('pink', 'Pink'),
        ('blue', 'Blue'),
        ('cream', 'Cream'),
        ('amber', 'Amber'),
    ]

    SCENT_CHOICES = [
        ('lavender', 'Lavender'),
        ('vanilla', 'Vanilla'),
        ('cinnamon', 'Cinnamon'),
        ('rose', 'Rose'),
        ('other', 'Other'),
        # Add more as needed
    ]

    SIZE_CHOICES = [
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
    ]

    title = models.CharField(
        max_length=255,
        help_text="Enter the title of the candle (e.g., 'Lavender Scented Candle')."
    )
    description = models.TextField(
        help_text="Provide a detailed description of the candle, including scent, mood, and usage."
    )
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text="Enter the regular price in USD (e.g., 19.99)."
    )
    discount_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Enter a discounted price if applicable; leave blank otherwise."
    )
    stock_quantity = models.PositiveIntegerField(
        default=0,
        help_text="Number of items in stock. This controls availability."
    )
    scent = models.CharField(
        max_length=50,
        choices=SCENT_CHOICES,
        help_text="Select the candle's scent."
    )
    color = models.CharField(
        max_length=50,
        choices=COLOR_CHOICES,
        help_text="Choose the candle's color."
    )
    size = models.CharField(
        max_length=50,
        choices=SIZE_CHOICES,
        help_text="Select the candle's size (small, medium, large)."
    )
    featured = models.BooleanField(
        default=False,
        help_text="Check to feature this candle on the homepage or special collections."
    )
    best_seller = models.BooleanField(
        default=False,
        help_text="Check if this is one of your top-selling candles."
    )
    image = models.ImageField(
        upload_to='products/',
        help_text="Upload a high-quality product image."
    )

    def __str__(self):
        return self.title


class WaxMelt(models.Model):
    COLOR_CHOICES = [
        ('white', 'White'),
        ('pink', 'Pink'),
        ('blue', 'Blue'),
        ('cream', 'Cream'),
        ('amber', 'Amber'),
    ]

    SCENT_CHOICES = [
        ('lavender', 'Lavender'),
        ('vanilla', 'Vanilla'),
        ('cinnamon', 'Cinnamon'),
        ('rose', 'Rose'),
        ('other', 'Other'),
        # Add more as needed
    ]

    SIZE_CHOICES = [
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
    ]

    title = models.CharField(
        max_length=255,
        help_text="Enter the name of the wax melt (e.g., 'Vanilla Bean Wax Melt')."
    )
    description = models.TextField(
        help_text="Write a description of the wax melt, including scent profile and usage suggestions."
    )
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text="Enter the standard price in USD (e.g., 7.99)."
    )
    discount_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Enter a discounted price if available, or leave blank."
    )
    stock_quantity = models.PositiveIntegerField(
        default=0,
        help_text="Total number of wax melts available in stock."
    )
    scent = models.CharField(
        max_length=50,
        choices=SCENT_CHOICES,
        help_text="Choose the scent of the wax melt."
    )
    color = models.CharField(
        max_length=50,
        choices=COLOR_CHOICES,
        help_text="Select the color of the wax melt."
    )
    size = models.CharField(
        max_length=50,
        choices=SIZE_CHOICES,
        help_text="Choose the size of the wax melt (e.g., Small pack, Medium, Large bundle)."
    )
    featured = models.BooleanField(
        default=False,
        help_text="Mark this wax melt as featured to highlight it on the homepage or in promotions."
    )
    best_seller = models.BooleanField(
        default=False,
        help_text="Mark this wax melt as a best-seller if it’s one of your top products."
    )
    image = models.ImageField(
        upload_to='products/',
        help_text="Upload a clear, high-resolution image of the wax melt."
    )

    def __str__(self):
        return self.title
