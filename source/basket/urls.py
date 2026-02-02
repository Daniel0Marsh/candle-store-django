from django.urls import path
from .views import (
    BasketPageView,
    UserDetailsPageView,
    StripePaymentView,
    PaymentConfirmationView,
)

urlpatterns = [
    path('basket/', BasketPageView.as_view(), name='basket'),
    path('checkout/details/', UserDetailsPageView.as_view(), name='user_details'),
    path('checkout/payment/', StripePaymentView.as_view(), name='stripe_payment'),
    path('checkout/success/', PaymentConfirmationView.as_view(), name='payment_success'),
]
