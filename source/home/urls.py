from django.urls import path
from . views import HomePageView, ProductSearchView, AboutPageView, PrivacyPolicyPageView, TermsOfServicePageView


urlpatterns = [
    path('', HomePageView.as_view(), name="home"),
    path('search/', ProductSearchView.as_view(), name='product_search'),
    path('about-us/', AboutPageView.as_view(), name='about'),
    path('privacy-policy/', PrivacyPolicyPageView.as_view(), name='privacy_policy'),
    path('terms-of-service/', TermsOfServicePageView.as_view(), name='terms_of_service'),
]
