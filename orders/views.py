from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import Order
from phones.models import Listing
import os
from dotenv import load_dotenv
from django.utils import timezone
from datetime import timedelta

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
            text += f"💳 Tur: {'Muddatli tolov' if is_installment else 'Naqd pul'}\n"
            if is_installment:
                text += f"🗓 Muddat: {months} oy\n"
                text += f"💵 Boshl. to'lov: {initial_payment} so'm\n"
            text += f"🚚 Yetkazib berish: {'Dastavka' if order.delivery_type == 'delivery' else 'Kelib olish'}\n"
            if order.address:
                text += f"📍 Manzil: {order.address}\n"
            
            try:
                import requests
                requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", data={
                    "chat_id": admin_id,
                    "text": text,
                    "parse_mode": "HTML"
                })
            except: pass

        # Mark listing as booked so it disappears from web app
        listing.is_booked = True
        listing.booked_until = timezone.now() + timedelta(hours=48)
        listing.save()

        return render(request, 'orders/success.html', {'order': order})

class CartOrderView(View):
    def post(self, request):
        import json
        import requests
        from django.http import JsonResponse
        
        try:
            data = json.loads(request.body)
            items = data.get('items', [])
            customer_name = data.get('name')
            customer_phone = data.get('phone')
            customer_telegram = data.get('telegram', '—')

            if not items or not customer_name or not customer_phone:
                return JsonResponse({"status": "error", "message": "Ma'lumotlar to'liq emas"}, status=400)

            # Validation: Phone should be at least 9 digits
            import re
            clean_phone = re.sub(r'\D', '', customer_phone)
            if len(clean_phone) < 9:
                 return JsonResponse({"status": "error", "message": "Telefon raqami noto'g'ri"}, status=400)

            load_dotenv()
            bot_token = os.environ.get('BOT_TOKEN')
            admin_id = os.environ.get('ADMIN_ID')
            
            summary_text = f"🔥 <b>YANGI BUYURTMA (SAVATCHADAN)</b>\n\n"
            summary_text += f"👤 Mijoz: <b>{customer_name}</b>\n"
            summary_text += f"📞 Tel: <code>{customer_phone}</code>\n"
            summary_text += f"✈️ Telegram: {customer_telegram}\n\n"
            summary_text += f"📦 <b>Tanlangan mahsulotlar:</b>\n"
            
            total_price = 0
            for item in items:
                listing = Listing.objects.filter(id=item['id']).first()
                if listing:
                    summary_text += f"• {listing.title} ({listing.price} $)\n"
                    total_price += float(listing.price)
                    
                    # Create Order record
                    Order.objects.create(
                        listing=listing,
                        customer_name=customer_name,
                        customer_phone=customer_phone,
                    )
                    # Optional: mark as booked
                    listing.is_booked = True
                    listing.booked_until = timezone.now() + timedelta(hours=48)
                    listing.save()

            summary_text += f"\n💰 <b>Jami: {total_price} $</b>"

            if bot_token and admin_id:
                requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", data={
                    "chat_id": admin_id,
                    "text": summary_text,
                    "parse_mode": "HTML"
                })

            return JsonResponse({"status": "ok"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
