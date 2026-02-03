from django.db import models
from django.utils.crypto import get_random_string
from products.models import Product


# orders/models.py
import uuid
from django.db import models
from django.utils.timezone import now

class Order(models.Model):

    STATUS_CHOICES = (
        ("pending", "Pending payment"),
        ("paid", "Paid"),
        ("failed", "Payment failed"),
        ("shipped", "Shipped"),
        ("refunded", "Refunded"),
    )

    reference = models.CharField(
        max_length=32,
        unique=True,
        editable=False,
    )

    email = models.EmailField()
    full_name = models.CharField(max_length=255)

    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    stripe_payment_intent = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    refunded_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    emails_sent_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = uuid.uuid4().hex.upper()[:10]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.reference}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE,
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
    )

    product_title = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    refunded_quantity = models.PositiveIntegerField(default=0)

    def line_total(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.product_title} x {self.quantity}"


class Shipment(models.Model):
    order = models.OneToOneField(
        Order,
        related_name="shipment",
        on_delete=models.CASCADE,
    )

    carrier = models.CharField(max_length=100)
    tracking_number = models.CharField(max_length=100, blank=True)
    estimated_delivery = models.DateField(null=True, blank=True)

    email_sent_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Shipment for {self.order.reference}"

