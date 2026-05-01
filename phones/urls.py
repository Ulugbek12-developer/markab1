from django.urls import path
from . import views

app_name = 'phones'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('filter/', views.FilterView.as_view(), name='filter'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('phone/<int:pk>/', views.PhoneDetailView.as_view(), name='detail'),
    path('calculator/', views.CalculatorView.as_view(), name='calculator'),
]
