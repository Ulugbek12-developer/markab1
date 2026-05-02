from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import Order
from phones.models import Listing

class CheckoutView(View):
    def get(self, request, listing_id):
        listing = get_object_or_404(Listing, pk=listing_id)
        payment_type = request.GET.get('payment_type', 'cash')
        months = request.GET.get('months', '')
        
        branches = [
            ("Malika", "📍 Malika"),
            ("Chilonzor", "📍 Chilonzor"),
        ]
        
        return render(request, 'orders/checkout.html', {
            'listing': listing,
            'payment_type': payment_type,
            'months': months,
            'branches': branches
        })

    def post(self, request, listing_id):
        listing = get_object_or_404(Listing, pk=listing_id)
        name = request.POST.get('name')
        user_phone = request.POST.get('phone')
        is_installment = request.POST.get('is_installment') == 'on'
        months = request.POST.get('months')

        Order.objects.create(
            listing=listing,
            customer_name=name,
            customer_phone=user_phone,
            is_installment=is_installment,
            installment_months=int(months) if months else None,
            delivery_type=request.POST.get('delivery_type', 'pickup'),
            branch=request.POST.get('branch'),
            address=request.POST.get('address')
        )
        return redirect('orders:success')

class SuccessView(View):
    def get(self, request):
        return render(request, 'orders/success.html')
