# basket/utils.py
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from decimal import Decimal
from products.models import Product, ProductSettings

def calculate_basket(basket):
    """
    Returns detailed basket info including products, totals, delivery,
    and remaining amount for free delivery.
    """
    products_list = []
    total = Decimal("0.00")

    for product_id, quantity in basket.items():
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            continue

        price = product.effective_price
        product_total = price * quantity

        products_list.append({
            "product": product,
            "quantity": quantity,
            "total": product_total,
            "discounted": bool(product.discount_price),
        })

        total += product_total

    pricing_settings = ProductSettings.objects.first()
    delivery_fee = Decimal("0.00")
    free_delivery_applied = False
    remaining_for_free_delivery = None

    if pricing_settings and pricing_settings.free_delivery_over:
        if total >= pricing_settings.free_delivery_over:
            free_delivery_applied = True
            delivery_fee = Decimal("0.00")
        else:
            free_delivery_applied = False
            delivery_fee = pricing_settings.delivery_fee
            remaining_for_free_delivery = pricing_settings.free_delivery_over - total
    elif pricing_settings:
        delivery_fee = pricing_settings.delivery_fee

    final_total = total + delivery_fee

    return {
        "products": products_list,
        "total": total,
        "delivery_fee": delivery_fee,
        "final_total": final_total,
        "free_delivery_applied": free_delivery_applied,
        "remaining_for_free_delivery": remaining_for_free_delivery,
        "item_count": sum(basket.values()),
    }
