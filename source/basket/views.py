from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from branding.models import Branding
from products.models import Candle, WaxMelt


class BasketPageView(TemplateView):
    template_name = 'basket.html'

    def get_context_data(self, **kwargs):
        """
        Get context data for the template.
        """
        basket = self.request.session.get('basket', {})

        # Get all products in the basket with details
        products = []
        total = 0
        for product_id, quantity in basket.items():
            try:
                product = Candle.objects.get(id=product_id)
            except Candle.DoesNotExist:
                try:
                    product = WaxMelt.objects.get(id=product_id)
                except WaxMelt.DoesNotExist:
                    continue  # Skip if the product doesn't exist
            product_total = (product.discount_price if product.discount_price else product.price) * quantity
            products.append({
                'product': product,
                'quantity': quantity,
                'total': product_total,
                'discounted': product.discount_price is not None
            })
            total += product_total

        # Apply any discounts or logic you might need to calculate (e.g., free shipping for orders over a certain amount)
        context = {
            "cart": {
                'item_count': sum(basket.values()),
                'products': products,
                'total': total,
            },
            "branding": Branding.objects.first(),
        }
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
