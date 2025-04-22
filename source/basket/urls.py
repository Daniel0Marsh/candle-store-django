from django.urls import path
from . views import BasketPageView, UserDetailsPageView, StripePaymentView, PaymentConfirmationView


urlpatterns = [
    path('basket', BasketPageView.as_view(), name="basket"),
    path('user-details/', UserDetailsPageView.as_view(), name='user_details'),
    path('payment/', StripePaymentView.as_view(), name='stripe_payment'),
    path('success/', PaymentConfirmationView.as_view(), name='payment_success'),
]
