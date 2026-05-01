from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from core.telegram_bot import send_admin_notification

@receiver(post_save, sender=Order)
def notify_admin_new_order(sender, instance, created, **kwargs):
    if created:
        status_txt = 'Ha' if instance.is_installment else "Yo'q"
        message = (
            f"🆕 <b>Yangi Buyurtma!</b>\n\n"
            f"👤 <b>Mijoz:</b> {instance.customer_name}\n"
            f"📞 <b>Telefon:</b> {instance.customer_phone}\n"
            f"📱 <b>Mahsulot:</b> {instance.phone.get_model_name_display()} ({instance.phone.memory}GB)\n"
            f"💰 <b>Narxi:</b> {float(instance.phone.price):,.0f} so'm\n"
            f"💳 <b>Muddatli to'lov:</b> {status_txt}\n"
        )
        if instance.is_installment:
            message += f"📅 <b>Muddati:</b> {instance.installment_months} oy\n"
        
        message += f"\n🚛 <b>Yetkazib berish:</b> {'Dastavka' if instance.delivery_type == 'delivery' else 'Kelib olib ketish'}\n"
        if instance.delivery_type == 'pickup':
            message += f"🏢 <b>Filial:</b> {instance.branch}\n"
        else:
            message += f"📍 <b>Manzil:</b> {instance.address}\n"
            
        message += f"\n🏷 <i>#MiniAppZakaz</i>"
        message += f"\n⏰ <b>Vaqt:</b> {instance.created_at.strftime('%Y-%m-%d %H:%M')}"
        
        send_admin_notification(message)
