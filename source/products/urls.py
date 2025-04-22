from django.urls import path
from . views import AllProductsPageView, CandlesPageView, WaxMeltsPageView, ProductDetailView


urlpatterns = [
    path('all-products', AllProductsPageView.as_view(), name="all_products"),
    path('candles/', CandlesPageView.as_view(), name='candles'),
    path('wax-melts/', WaxMeltsPageView.as_view(), name='wax_melts'),
    path('product/<str:product_type>/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
]
