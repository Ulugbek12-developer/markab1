from django.urls import path
from phones import views

app_name = 'phones'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('filter/', views.FilterView.as_view(), name='filter'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('phone/<int:pk>/', views.PhoneDetailView.as_view(), name='detail'),
    path('phone/<int:pk>/book/', views.BookPhoneView.as_view(), name='book'),
    path('calculator/', views.CalculatorView.as_view(), name='calculator'),
    path('markab-admin/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('markab-admin/add/', views.AdminAddPhoneView.as_view(), name='admin_add'),
    path('markab-admin/delete/<int:pk>/', views.AdminDeletePhoneView.as_view(), name='admin_delete'),
]
