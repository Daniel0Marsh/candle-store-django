from django.views.generic import ListView, DetailView
from django.db.models import Q, F
from django.shortcuts import redirect
from django.utils import timezone

from products.models import Product
from home.models import HomePage


class ProductListView(ListView):
    model = Product
    template_name = "products.html"
    context_object_name = "products"
    paginate_by = 12

    # ----- Page config -----
    page_title = "All Products"
    product_type_filter = None
    special_filter = None

    def get_queryset(self):
        qs = Product.objects.all()

        # ----- Product type filter -----
        if self.product_type_filter:
            qs = qs.filter(product_type=self.product_type_filter)

        # ----- Special filters -----
        if self.special_filter == "offers":
            qs = qs.filter(discount_price__gt=0, discount_price__lt=F('price'))
        elif self.special_filter == "new":
            last_week = timezone.now() - timezone.timedelta(days=7)
            qs = qs.filter(created_at__gte=last_week)

        # ----- GET filters for search form -----
        search = self.request.GET.get("search", "").strip()
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))

        scent = self.request.GET.get("scent")
        if scent:
            qs = qs.filter(scent=scent)

        size = self.request.GET.get("size")
        if size:
            qs = qs.filter(size=size)

        color = self.request.GET.get("color")
        if color:
            qs = qs.filter(color=color)

        price = self.request.GET.get("price")
        if price:
            try:
                price_val = float(price)
                qs = qs.filter(price__lte=price_val)
            except ValueError:
                pass

        return qs.order_by("title")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "page_title": self.page_title,
            "home": HomePage.objects.first(),
            "selected": {
                "search": self.request.GET.get("search", ""),
                "scent": self.request.GET.get("scent", ""),
                "size": self.request.GET.get("size", ""),
                "color": self.request.GET.get("color", ""),
                "price": self.request.GET.get("price", ""),
                "type": self.product_type_filter,
            },
            "scent_choices": Product.Scent.choices,
            "size_choices": Product.Size.choices,
            "color_choices": Product.Color.choices,
            "query": self.request.GET.get("q", "").strip() or self.request.GET.get("search", "")
        })
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = "product_detail.html"
    slug_field = "slug"
    slug_url_kwarg = "product_slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "home": HomePage.objects.first(),
            "meta": self.object.meta,
        })
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        quantity = max(1, int(request.POST.get("quantity", 1)))

        basket = request.session.get("basket", {})
        key = str(self.object.pk)
        basket[key] = basket.get(key, 0) + quantity

        request.session["basket"] = basket
        return redirect(self.object.get_absolute_url())
