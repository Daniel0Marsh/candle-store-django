from django.urls import path
from . views import ContactPageView


urlpatterns = [
    path('contact/', ContactPageView.as_view(), name="contact"),
]
