
from .models import Product, ProductSettings


def product_context(request):
    return {
        "products": Product.objects.all(),
        "featured_products": Product.objects.filter(featured=True),
        "best_sellers": Product.objects.filter(best_seller=True),
        "products_settings": ProductSettings.objects.first(),
    }
