from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap, ProductSitemap

# Sitemap dict
sitemaps_dict = {
    'static': StaticViewSitemap,
    'products': ProductSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('products.urls')),
    path('', include('basket.urls')),
    path('', include('contact.urls')),
    path('', include('home.urls')),
    path("ckeditor5/", include('django_ckeditor_5.urls')),

    # Sitemap
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps_dict}, name='django-sitemap'),
]

# Serve media + static in development
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin branding
admin.site.site_header = "Welcome to Lelsea's Melts Admin"
admin.site.site_title = "Lelsea's Melts"
admin.site.index_title = "Welcome to the admin area"
