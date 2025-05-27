from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect
from itertools import chain
from .models import Candle, WaxMelt
from branding.models import Branding


class AllProductsPageView(TemplateView):
    """Displays all candles and wax melts with filter and search options."""

    template_name = 'all_products.html'

    def get_context_data(self, **kwargs):
        """Collects and filters all products and returns them in the context."""
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

        basket = request.session.get('basket', {})
        item_count = sum(basket.values())

        context.update({
            'cart': {'item_count': item_count},
            'branding': Branding.objects.first(),
            'products': products,
            'scent_choices': Candle.SCENT_CHOICES,
            'color_choices': Candle.COLOR_CHOICES,
            'size_choices': Candle.SIZE_CHOICES,
        })
        return context


class CandlesPageView(TemplateView):
    """Displays filtered list of candle products."""

    template_name = 'candles.html'

    def get_context_data(self, **kwargs):
        """Filters and returns candle products in the context."""
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
                pass

        basket = request.session.get('basket', {})
        item_count = sum(basket.values())

        context.update({
            'cart': {'item_count': item_count},
            'branding': Branding.objects.first(),
            'candles': candles,
            'scent_choices': Candle.SCENT_CHOICES,
            'color_choices': Candle.COLOR_CHOICES,
            'size_choices': Candle.SIZE_CHOICES,
        })
        return context


class WaxMeltsPageView(TemplateView):
    """Displays filtered list of wax melt products."""

    template_name = 'wax_melts.html'

    def get_context_data(self, **kwargs):
        """Filters and returns wax melt products in the context."""
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
                pass

        basket = request.session.get('basket', {})
        item_count = sum(basket.values())

        context.update({
            'cart': {'item_count': item_count},
            'branding': Branding.objects.first(),
            'wax_melts': wax_melts,
            'scent_choices': WaxMelt.SCENT_CHOICES,
            'color_choices': WaxMelt.COLOR_CHOICES,
            'size_choices': WaxMelt.SIZE_CHOICES,
        })
        return context


class ProductDetailView(TemplateView):
    """Displays product detail page for a candle or wax melt."""

    template_name = 'product_detail.html'

    def get_context_data(self, **kwargs):
        """Returns the selected product detail in the context."""
        context = super().get_context_data(**kwargs)
        product_type = self.kwargs.get('product_type')
        pk = self.kwargs.get('pk')

        if product_type == 'candle':
            product = get_object_or_404(Candle, pk=pk)
        elif product_type == 'waxmelt':
            product = get_object_or_404(WaxMelt, pk=pk)
        else:
            raise ValueError("Invalid product type")

        basket = self.request.session.get('basket', {})
        item_count = sum(basket.values())

        context.update({
            'product': product,
            'branding': Branding.objects.first(),
            'product_type': product_type,
            'cart': {'item_count': item_count},
        })
        return context

    def post(self, request, *args, **kwargs):
        """Handles adding the product to the basket."""
        product_type = self.kwargs.get('product_type')
        pk = self.kwargs.get('pk')

        if product_type == 'candle':
            product = get_object_or_404(Candle, pk=pk)
        elif product_type == 'waxmelt':
            product = get_object_or_404(WaxMelt, pk=pk)
        else:
            raise ValueError("Invalid product type")

        quantity = int(request.POST.get('quantity', 1))
        basket = request.session.get('basket', {})

        if str(product.pk) in basket:
            basket[str(product.pk)] += quantity
        else:
            basket[str(product.pk)] = quantity

        request.session['basket'] = basket
        request.session['item_count'] = sum(basket.values())

        return redirect('product_detail', product_type=product_type, pk=pk)
