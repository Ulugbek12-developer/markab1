from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('sell/', views.SellPhoneView.as_view(), name='sell'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
]
