from django.db import transaction
from products.models import Product
from .models import Order, OrderItem


@transaction.atomic
def create_order_from_basket(*, basket, user_info, pricing):
    """
    Create an Order + OrderItems from session basket.

    basket: {product_id (str|int): quantity}
    user_info: dict from session
    pricing: output of calculate_basket()
    """

    order = Order.objects.create(
        full_name=user_info["full_name"],
        email=user_info["email"],
        address_line1=user_info["address_line1"],
        address_line2=user_info.get("address_line2", ""),
        city=user_info["city"],
        postal_code=user_info["postal_code"],
        country=user_info["country"],
        subtotal=pricing["total"],
        delivery_fee=pricing["delivery_fee"],
        total=pricing["final_total"],
    )

    for raw_product_id, quantity in basket.items():
        product_id = int(raw_product_id)

        try:
            product = (
                Product.objects
                .select_for_update()
                .get(pk=product_id)
            )
        except Product.DoesNotExist:
            raise ValueError(f"Product {product_id} no longer exists")

        if quantity <= 0:
            continue

        OrderItem.objects.create(
            order=order,
            product=product,
            product_title=product.title,
            unit_price=product.effective_price,
            quantity=quantity,
        )

    return order


# orders/services.py
from django.db import transaction
from products.models import Product
from .models import Order

def mark_order_as_paid(order: Order, payment_intent_id: str):
    """
    Idempotent order finalisation.
    Safe to call multiple times.
    """

    if order.status == "paid":
        return

    with transaction.atomic():
        order.status = "paid"
        order.stripe_payment_intent = payment_intent_id
        order.save(update_fields=["status", "stripe_payment_intent", "updated_at"])

        for item in order.items.select_for_update():
            product = item.product
            product.stock_quantity = max(
                product.stock_quantity - item.quantity,
                0
            )
            product.save(update_fields=["stock_quantity"])
