from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect
from itertools import chain
from .models import Candle, WaxMelt
from branding.models import Branding


class AllProductsPageView(TemplateView):
    template_name = 'all_products.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request

        search_query = request.GET.get('search', '')
        scent = request.GET.get('scent', '')
        size = request.GET.get('size', '')
        color = request.GET.get('color', '')
        max_price = request.GET.get('price', '')

        candles = Candle.objects.all()
        wax_melts = WaxMelt.objects.all()

        if search_query:
            candles = candles.filter(title__icontains=search_query)
            wax_melts = wax_melts.filter(title__icontains=search_query)

        if scent:
            candles = candles.filter(scent=scent)
            wax_melts = wax_melts.filter(scent=scent)

        if size:
            candles = candles.filter(size=size)
            wax_melts = wax_melts.filter(size=size)

        if color:
            candles = candles.filter(color=color)
            wax_melts = wax_melts.filter(color=color)

        if max_price:
            try:
                max_price_float = float(max_price)
                candles = candles.filter(price__lte=max_price_float)
                wax_melts = wax_melts.filter(price__lte=max_price_float)
            except ValueError:
                pass

        # Merge both into one queryset-like list
        products = sorted(
            chain(candles, wax_melts),
            key=lambda p: p.pk,
            reverse=True
        )

        for product in products:
            if isinstance(product, Candle):
                product.product_type = 'candle'
            elif isinstance(product, WaxMelt):
                product.product_type = 'waxmelt'

        # Get the current shopping basket from the session
        basket = self.request.session.get('basket', {})

        # Calculate the total item count in the basket
        item_count = sum(basket.values())

        context['cart'] = {'item_count': item_count}
        context['branding'] = Branding.objects.first()
        context['products'] = products
        context['scent_choices'] = Candle.SCENT_CHOICES
        context['color_choices'] = Candle.COLOR_CHOICES
        context['size_choices'] = Candle.SIZE_CHOICES
        return context


class CandlesPageView(TemplateView):
    template_name = 'candles.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request

        search_query = request.GET.get('search', '')
        scent = request.GET.get('scent', '')
        size = request.GET.get('size', '')
        color = request.GET.get('color', '')
        max_price = request.GET.get('price', '')

        candles = Candle.objects.all()

        if search_query:
            candles = candles.filter(title__icontains=search_query)

        if scent:
            candles = candles.filter(scent=scent)

        if size:
            candles = candles.filter(size=size)

        if color:
            candles = candles.filter(color=color)

        if max_price:
            try:
                candles = candles.filter(price__lte=float(max_price))
            except ValueError:
                pass  # Ignore invalid price input

        # Get the current shopping basket from the session
        basket = self.request.session.get('basket', {})

        # Calculate the total item count in the basket
        item_count = sum(basket.values())

        context['cart'] = {'item_count': item_count}
        context['branding'] = Branding.objects.first()
        context['candles'] = candles
        context['scent_choices'] = Candle.SCENT_CHOICES
        context['color_choices'] = Candle.COLOR_CHOICES
        context['size_choices'] = Candle.SIZE_CHOICES
        return context


class WaxMeltsPageView(TemplateView):
    template_name = 'wax_melts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request

        search_query = request.GET.get('search', '')
        scent = request.GET.get('scent', '')
        size = request.GET.get('size', '')
        color = request.GET.get('color', '')
        max_price = request.GET.get('price', '')

        wax_melts = WaxMelt.objects.all()

        if search_query:
            wax_melts = wax_melts.filter(title__icontains=search_query)

        if scent:
            wax_melts = wax_melts.filter(scent=scent)

        if size:
            wax_melts = wax_melts.filter(size=size)

        if color:
            wax_melts = wax_melts.filter(color=color)

        if max_price:
            try:
                wax_melts = wax_melts.filter(price__lte=float(max_price))
            except ValueError:
                pass  # Ignore invalid price input

        # Get the current shopping basket from the session
        basket = self.request.session.get('basket', {})

        # Calculate the total item count in the basket
        item_count = sum(basket.values())

        context['cart'] = {'item_count': item_count}
        context['branding'] = Branding.objects.first()
        context['wax_melts'] = wax_melts
        context['scent_choices'] = WaxMelt.SCENT_CHOICES
        context['color_choices'] = WaxMelt.COLOR_CHOICES
        context['size_choices'] = WaxMelt.SIZE_CHOICES
        return context


class ProductDetailView(TemplateView):
    template_name = 'product_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_type = self.kwargs.get('product_type')
        pk = self.kwargs.get('pk')

        if product_type == 'candle':
            product = get_object_or_404(Candle, pk=pk)
        elif product_type == 'waxmelt':
            product = get_object_or_404(WaxMelt, pk=pk)
        else:
            raise ValueError("Invalid product type")

        # Get the current shopping basket from the session
        basket = self.request.session.get('basket', {})

        # Calculate the total item count in the basket
        item_count = sum(basket.values())

        # Pass cart item count to context
        context['product'] = product
        context['branding'] = Branding.objects.first()
        context['product_type'] = product_type
        context['cart'] = {'item_count': item_count}
        return context

    def post(self, request, *args, **kwargs):
        product_type = self.kwargs.get('product_type')
        pk = self.kwargs.get('pk')

        if product_type == 'candle':
            product = get_object_or_404(Candle, pk=pk)
        elif product_type == 'waxmelt':
            product = get_object_or_404(WaxMelt, pk=pk)
        else:
            raise ValueError("Invalid product type")

        # Get the quantity from the form, default to 1
        quantity = int(request.POST.get('quantity', 1))

        # Get the current shopping basket from the session
        basket = request.session.get('basket', {})

        # Update the basket with the new product and quantity
        if str(product.pk) in basket:
            basket[str(product.pk)] += quantity  # Update quantity if product is already in the basket
        else:
            basket[str(product.pk)] = quantity  # Add new product to the basket

        # Save the updated basket back to the session
        request.session['basket'] = basket

        # Recalculate the item count in the basket
        item_count = sum(basket.values())

        # Save the item count to session for cart display
        request.session['item_count'] = item_count

        # Redirect back to the product detail page or another page
        return redirect('product_detail', product_type=product_type, pk=pk)

