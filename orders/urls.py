from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/<int:listing_id>/', views.CheckoutView.as_view(), name='checkout'),
    path('cart-order/', views.CartOrderView.as_view(), name='cart_order'),
    path('success/', views.TemplateView.as_view(template_name='orders/success.html'), name='success'),
]
