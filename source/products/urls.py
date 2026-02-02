from django.urls import path
from .views import ProductListView, ProductDetailView

urlpatterns = [
    path("products/", ProductListView.as_view(), name="products"),
    path("products/candles/", ProductListView.as_view(
        page_title="Candles", product_type_filter="candle"
    ), name="product_candles"),
    path("products/waxmelts/", ProductListView.as_view(
        page_title="Wax Melts", product_type_filter="waxmelt"
    ), name="product_waxmelts"),
    path("products/gifts/", ProductListView.as_view(
        page_title="Gifts", product_type_filter="gift"
    ), name="product_gifts"),
    path("products/offers/", ProductListView.as_view(
        page_title="Special Offers", special_filter="offers"
    ), name="product_offers"),
    path("products/new/", ProductListView.as_view(
        page_title="New Arrivals", special_filter="new"
    ), name="product_new"),
    path("product/<slug:product_slug>/", ProductDetailView.as_view(), name="product_detail"),
]
