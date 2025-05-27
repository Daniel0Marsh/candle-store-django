from django.db import models


class StorePricingSettings(models.Model):
    """
    Stores global pricing settings for the store, including delivery fees and free delivery thresholds.

    Fields:
        delivery_fee (DecimalField): Flat rate delivery fee applied to all orders.
        free_delivery_over (DecimalField, optional): Basket total threshold for free delivery; null/blank disables it.
        updated_at (DateTimeField): Auto-updated timestamp for when the settings were last modified.
    """

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
    """
    Represents a single candle product available for purchase.

    Fields:
        title (CharField): The name/title of the candle.
        description (TextField): A rich description including scent, usage, and appeal.
        price (DecimalField): Standard price in USD.
        discount_price (DecimalField, optional): Discounted price if applicable.
        stock_quantity (PositiveIntegerField): Number of items currently in stock.
        scent (CharField): Selected scent from predefined choices.
        color (CharField): Chosen candle color from available options.
        size (CharField): Selected size (small, medium, large).
        featured (BooleanField): Marks candle for homepage or special display.
        best_seller (BooleanField): Indicates if this is a top-selling product.
        image (ImageField): High-quality image of the candle.
    """

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
    """
    Represents a single wax melt product for sale in the store.

    Fields:
        title (CharField): The name/title of the wax melt.
        description (TextField): Detailed overview including scent and usage tips.
        price (DecimalField): Standard selling price in USD.
        discount_price (DecimalField, optional): Optional reduced price.
        stock_quantity (PositiveIntegerField): Number in stock.
        scent (CharField): Chosen fragrance from defined options.
        color (CharField): Selected product color.
        size (CharField): Chosen size variant (small, medium, large).
        featured (BooleanField): Flags item as featured for promotion.
        best_seller (BooleanField): Identifies top-performing wax melt.
        image (ImageField): Uploaded image to visually represent the product.
    """

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
