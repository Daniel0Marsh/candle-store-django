from django.urls import path
from . views import BasketPageView


urlpatterns = [
    path('basket', BasketPageView.as_view(), name="basket"),
]
