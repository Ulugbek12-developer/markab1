from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import Order
from phones.models import Listing
import requests
import os
from dotenv import load_dotenv

class CheckoutView(View):
    def get(self, request, listing_id):
        listing = get_object_or_404(Listing, pk=listing_id)
        payment_type = request.GET.get('type', 'cash')
        
        return render(request, 'orders/checkout.html', {
            'listing': listing,
            'payment_type': payment_type,
        })

    def post(self, request, listing_id):
        listing = get_object_or_404(Listing, pk=listing_id)
        name = request.POST.get('name')
        user_phone = request.POST.get('phone')
        is_installment = request.POST.get('is_installment') == 'on'
        months = request.POST.get('months')
        initial_payment = request.POST.get('initial_payment', 0)

        order = Order.objects.create(
            listing=listing,
            customer_name=name,
            customer_phone=user_phone,
            is_installment=is_installment,
            installment_months=int(months) if months and months.isdigit() else None,
            initial_payment=initial_payment if initial_payment else 0,
            delivery_type=request.POST.get('delivery_type', 'pickup'),
            address=request.POST.get('address')
        )

        # Telegram Notification
        load_dotenv()
        bot_token = os.environ.get('BOT_TOKEN')
        admin_id = os.environ.get('ADMIN_ID')
        if bot_token and admin_id:
            text = f"🛍 <b>Yangi Buyurtma! #{order.id}</b>\n\n"
            text += f"📱 Telefon: {listing.title}\n"
            text += f"💰 Narxi: {listing.price} so'm\n\n"
            text += f"👤 Mijoz: {name}\n"
            text += f"📞 Tel: {user_phone}\n"
            text += f"💳 Tur: {'Muddatli to\'lov' if is_installment else 'Naqd pul'}\n"
            if is_installment:
                text += f"🗓 Muddat: {months} oy\n"
                text += f"💵 Boshl. to'lov: {initial_payment} so'm\n"
            text += f"🚚 Yetkazib berish: {'Dastavka' if order.delivery_type == 'delivery' else 'Kelib olish'}\n"
            if order.address:
                text += f"📍 Manzil: {order.address}\n"
            
            try:
                requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", data={
                    "chat_id": admin_id,
                    "text": text,
                    "parse_mode": "HTML"
                })
            except: pass

        return render(request, 'orders/success.html', {'order': order})

class SuccessView(View):
    def get(self, request):
        return render(request, 'orders/success.html')
