from django.urls import path
from orders import views

app_name = 'orders'

urlpatterns = [
    path('checkout/<int:phone_id>/', views.CheckoutView.as_view(), name='checkout'),
    path('success/', views.SuccessView.as_view(), name='success'),
]
