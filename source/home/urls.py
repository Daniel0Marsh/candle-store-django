from django.urls import path
from . views import HomePageView, PolicyPageView

urlpatterns = [
    path('', HomePageView.as_view(), name="home"),
    path("<str:policy_type>/", PolicyPageView.as_view(), name="policy_page"),
]
