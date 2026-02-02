from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from products.models import Product
from django.utils import timezone

# -----------------------------
# Static pages sitemap
# -----------------------------
class StaticViewSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.8

    def items(self):
        # All static pages by URL name
        return [
            'home',
            'products',
            'product_candles',
            'product_waxmelts',
            'product_gifts',
            'product_offers',
            'product_new',
            'basket',
            'user_details',
            'stripe_payment',
            'payment_success',
            'contact',
            'policy_page',  # will resolve /privacy-policy/, /terms-of-service/, etc dynamically
        ]

    def location(self, item):
        # For policy_page, we need a default parameter (privacy-policy) just for sitemap
        if item == 'policy_page':
            return reverse(item, kwargs={'policy_type': 'privacy-policy'})
        return reverse(item)

    def lastmod(self, item):
        return timezone.now()


# -----------------------------
# Dynamic products sitemap
# -----------------------------
class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Product.objects.filter(stock_quantity__gt=0)

    def location(self, obj):
        return obj.get_absolute_url()

    def lastmod(self, obj):
        return obj.updated_at
