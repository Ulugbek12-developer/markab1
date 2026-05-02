from django.urls import path
from phones import views

app_name = 'phones'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('listing/<int:pk>/', views.ListingDetailView.as_view(), name='detail'),
    path('sell/', views.SellView.as_view(), name='sell'),
    path('price/', views.PriceView.as_view(), name='price'),
    path('favorites/', views.FavoritesView.as_view(), name='favorites'),
    path('favorite/<int:pk>/toggle/', views.ToggleFavoriteView.as_view(), name='toggle_favorite'),
    path('store-panel/', views.StorePanelView.as_view(), name='store_panel'),
    path('installment-request/<int:pk>/', views.InstallmentRequestView.as_view(), name='installment_request'),
]
