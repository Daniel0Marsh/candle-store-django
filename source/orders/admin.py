# orders/admin.py
from django.contrib import admin, messages
from django.utils.timezone import now
from django.urls import path
from django.shortcuts import redirect
from django.utils.html import format_html

from .models import Order, OrderItem, Shipment
from .emails import send_order_emails, send_shipping_email


# --------------------------------------------------
# INLINES
# --------------------------------------------------

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False

    readonly_fields = (
        "product",
        "product_title",
        "unit_price",
        "quantity",
        "refunded_quantity",
    )

    def has_add_permission(self, request, obj=None):
        return False


class ShipmentInline(admin.StackedInline):
    model = Shipment
    extra = 0
    max_num = 1

    readonly_fields = (
        "email_sent_at",
        "created_at",
    )

    fieldsets = (
        ("Shipment details", {
            "fields": (
                "carrier",
                "tracking_number",
                "estimated_delivery",
            )
        }),
        ("Email audit", {
            "fields": (
                "email_sent_at",
                "created_at",
            )
        }),
    )


# --------------------------------------------------
# ORDER ADMIN
# --------------------------------------------------

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Single control surface for:
    - order lifecycle
    - fulfilment
    - email communications
    """

    list_display = (
        "reference",
        "full_name",
        "email",
        "status",
        "total",
        "created_at",
    )

    list_filter = ("status", "created_at")
    search_fields = ("reference", "email", "full_name")
    ordering = ("-created_at",)

    inlines = [OrderItemInline, ShipmentInline]

    # -----------------------------
    # FIELD LOCKDOWN
    # -----------------------------

    readonly_fields = (
        # System
        "reference",
        "stripe_payment_intent",

        # Customer (LOCKED)
        "full_name",
        "email",

        # Address (LOCKED)
        "address_line1",
        "address_line2",
        "city",
        "postal_code",
        "country",

        # Financials (LOCKED)
        "subtotal",
        "delivery_fee",
        "total",

        # Audit
        "emails_sent_at",
        "created_at",
        "updated_at",
        "refunded_at",

        # Actions
        "email_actions",
    )

    fieldsets = (
        ("Order", {
            "fields": (
                "reference",
                "status",
                "stripe_payment_intent",
            )
        }),
        ("Customer (read-only)", {
            "fields": (
                "full_name",
                "email",
            )
        }),
        ("Delivery address (read-only)", {
            "fields": (
                "address_line1",
                "address_line2",
                "city",
                "postal_code",
                "country",
            )
        }),
        ("Totals (read-only)", {
            "fields": (
                "subtotal",
                "delivery_fee",
                "total",
            )
        }),
        ("Actions", {
            "fields": ("email_actions",),
        }),
        ("Email audit", {
            "fields": ("emails_sent_at",),
        }),
        ("Timestamps", {
            "fields": (
                "created_at",
                "updated_at",
                "refunded_at",
            )
        }),
    )

    # -----------------------------
    # CUSTOM URLS (BUTTON ACTIONS)
    # -----------------------------

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:object_id>/resend-confirmation/",
                self.admin_site.admin_view(self.resend_confirmation_view),
                name="orders_order_resend_confirmation",
            ),
            path(
                "<int:object_id>/resend-shipping/",
                self.admin_site.admin_view(self.resend_shipping_view),
                name="orders_order_resend_shipping",
            ),
        ]
        return custom_urls + urls


    # -----------------------------
    # PERMISSIONS
    # -----------------------------

    def has_delete_permission(self, request, obj=None):
        return False  # orders are immutable records

    # -----------------------------
    # EMAIL BUTTON UI
    # -----------------------------

    def email_actions(self, obj):
        buttons = [
            '<a class="button" href="../resend-confirmation/">Resend confirmation email</a>',
        ]

        if hasattr(obj, "shipment"):
            buttons.append(
                '<a class="button" href="../resend-shipping/">Resend shipping email</a>'
            )

        return format_html(" ".join(buttons))


    email_actions.short_description = "Email actions"

    # --------------------------------------------------
    # BUTTON HANDLERS
    # --------------------------------------------------

    def resend_confirmation_view(self, request, object_id):
        order = self.get_object(request, object_id)

        if not order:
            self.message_user(
                request,
                "Order not found.",
                messages.ERROR,
            )
            return redirect("admin:orders_order_changelist")

        send_order_emails(order, force=True)
        order.emails_sent_at = now()
        order.save(update_fields=["emails_sent_at", "updated_at"])

        self.message_user(
            request,
            "Order confirmation email resent.",
            messages.SUCCESS,
        )
        return redirect("admin:orders_order_change", object_id)


    def resend_shipping_view(self, request, object_id):
        order = self.get_object(request, object_id)

        if not hasattr(order, "shipment"):
            self.message_user(
                request,
                "No shipment exists for this order.",
                messages.ERROR,
            )
            return redirect("admin:orders_order_change", object_id)

        send_shipping_email(order)

        order.shipment.email_sent_at = now()
        order.shipment.save(update_fields=["email_sent_at"])

        self.message_user(
            request,
            "Shipping email resent.",
            messages.SUCCESS,
        )
        return redirect("admin:orders_order_change", object_id)

    # --------------------------------------------------
    # BULK ACTIONS
    # --------------------------------------------------

    actions = (
        "send_order_confirmation",
        "mark_as_shipped_and_send_email",
        "resend_shipping_email",
        "mark_as_refunded",
    )

    @admin.action(description="Send / resend order confirmation email")
    def send_order_confirmation(self, request, queryset):
        sent = 0

        for order in queryset:
            send_order_emails(order, force=True)
            order.emails_sent_at = now()
            order.save(update_fields=["emails_sent_at", "updated_at"])
            sent += 1

        self.message_user(
            request,
            f"Order confirmation email sent for {sent} order(s).",
            messages.SUCCESS,
        )

    @admin.action(description="Mark as shipped and send shipping email")
    def mark_as_shipped_and_send_email(self, request, queryset):
        queryset = queryset.select_related("shipment")

        sent = 0
        skipped = 0

        for order in queryset:
            if not hasattr(order, "shipment"):
                skipped += 1
                continue

            if order.shipment.email_sent_at:
                skipped += 1
                continue

            order.status = "shipped"
            order.save(update_fields=["status", "updated_at"])

            send_shipping_email(order)

            order.shipment.email_sent_at = now()
            order.shipment.save(update_fields=["email_sent_at"])

            sent += 1

        if sent:
            self.message_user(
                request,
                f"{sent} order(s) marked as shipped and email sent.",
                messages.SUCCESS,
            )

        if skipped:
            self.message_user(
                request,
                f"{skipped} order(s) skipped (no shipment or already emailed).",
                messages.WARNING,
            )

    @admin.action(description="Resend shipping email (does not change status)")
    def resend_shipping_email(self, request, queryset):
        queryset = queryset.select_related("shipment")

        sent = 0
        skipped = 0

        for order in queryset:
            if not hasattr(order, "shipment"):
                skipped += 1
                continue

            send_shipping_email(order)

            order.shipment.email_sent_at = now()
            order.shipment.save(update_fields=["email_sent_at"])

            sent += 1

        if sent:
            self.message_user(
                request,
                f"Shipping email resent for {sent} order(s).",
                messages.SUCCESS,
            )

        if skipped:
            self.message_user(
                request,
                f"{skipped} order(s) skipped (no shipment).",
                messages.WARNING,
            )

    @admin.action(description="Mark as refunded (no emails sent)")
    def mark_as_refunded(self, request, queryset):
        updated = 0

        for order in queryset:
            if order.status == "refunded":
                continue

            order.status = "refunded"
            order.refunded_at = now()
            order.save(update_fields=["status", "refunded_at", "updated_at"])
            updated += 1

        self.message_user(
            request,
            f"{updated} order(s) marked as refunded.",
            messages.SUCCESS,
        )
