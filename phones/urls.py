from django.urls import path
from . import views

app_name = 'phones'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('listing/<int:pk>/', views.ListingDetailView.as_view(), name='detail'),
    path('sell/', views.SellView.as_view(), name='sell'),
    path('price/', views.PriceView.as_view(), name='price'),
    path('favorites/', views.FavoritesView.as_view(), name='favorites'),
    path('favorite/<int:pk>/toggle/', views.ToggleFavoriteView.as_view(), name='toggle_favorite'),
    path('admin-dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin-dashboard/add/', views.StorePanelView.as_view(), name='admin_add'),
    path('admin-dashboard/delete/<int:pk>/', views.AdminDeleteView.as_view(), name='admin_delete'),
    path('installment-request/<int:pk>/', views.InstallmentRequestView.as_view(), name='installment_request'),
    path('toggle-booking/<int:pk>/', views.ToggleBookingView.as_view(), name='toggle_booking'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('catalog/', views.FilterView.as_view(), name='filter'),
    path('webhook/telegram/', views.telegram_webhook, name='telegram_webhook'),
]
