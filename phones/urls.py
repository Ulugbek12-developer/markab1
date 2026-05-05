from django.urls import path
from . import views

app_name = 'phones'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('catalog/', views.CatalogView.as_view(), name='catalog'),
    path('listing/<int:pk>/', views.ListingDetailView.as_view(), name='detail'),
    path('sell/', views.SellView.as_view(), name='sell'),
    path('price/', views.PriceView.as_view(), name='price'),
    path('trade-in/', views.TradeInView.as_view(), name='trade_in'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('favorites/', views.FavoritesView.as_view(), name='favorites'),
    path('favorite/<int:pk>/toggle/', views.ToggleFavoriteView.as_view(), name='toggle_favorite'),
    path('markab-master-panel-6969/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('markab-master-panel-6969/add/', views.StorePanelView.as_view(), name='admin_add'),
    path('markab-master-panel-6969/branch/add/', views.AdminBranchCreateView.as_view(), name='admin_branch_add'),
    path('markab-master-panel-6969/branch/delete/<int:pk>/', views.AdminBranchDeleteView.as_view(), name='admin_branch_delete'),
    path('markab-master-panel-6969/delete/<int:pk>/', views.AdminDeleteView.as_view(), name='admin_delete'),
    path('installment-request/<int:pk>/', views.InstallmentRequestView.as_view(), name='installment_request'),
    path('toggle-booking/<int:pk>/', views.ToggleBookingView.as_view(), name='toggle_booking'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('catalog/', views.FilterView.as_view(), name='filter'),
    path('listing/<int:pk>/review/', views.AddReviewView.as_view(), name='add_review'),
]
