from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from branding.models import Branding
from products.models import Candle, WaxMelt, StorePricingSettings


from decimal import Decimal

class BasketPageView(TemplateView):
    template_name = 'basket.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        basket = self.request.session.get('basket', {})

        products = []
        total = Decimal("0.00")
        for product_id, quantity in basket.items():
            try:
                product = Candle.objects.get(id=product_id)
            except Candle.DoesNotExist:
                try:
                    product = WaxMelt.objects.get(id=product_id)
                except WaxMelt.DoesNotExist:
                    continue
            price = product.discount_price if product.discount_price else product.price
            product_total = price * quantity
            products.append({
                'product': product,
                'quantity': quantity,
                'total': product_total,
                'discounted': product.discount_price is not None
            })
            total += product_total

        pricing_settings = StorePricingSettings.objects.first()
        delivery_fee = Decimal("0.00")

        if pricing_settings:
            if not pricing_settings.free_delivery_over or total < pricing_settings.free_delivery_over:
                delivery_fee = pricing_settings.delivery_fee

        context.update({
            "cart": {
                'item_count': sum(basket.values()),
                'products': products,
                'total': total,
                'final_total': total + delivery_fee,
                'delivery_fee': delivery_fee,
                'free_delivery_applied': pricing_settings.free_delivery_over and total >= pricing_settings.free_delivery_over
            },
            "pricing_settings": pricing_settings,
            "branding": Branding.objects.first(),
        })
        return context

    def post(self, request, *args, **kwargs):
        """
        Handle adding/removing items or updating quantities in the basket.
        """
        action = request.POST.get('action')
        product_id = request.POST.get('product_id')
        basket = request.session.get('basket', {})

        if action == 'remove':
            basket.pop(product_id, None)
        elif action == 'update':
            new_quantity = int(request.POST.get('quantity', 1))
            if new_quantity <= 0:
                basket.pop(product_id, None)
            else:
                basket[product_id] = new_quantity

        request.session['basket'] = basket
        return redirect('basket')
