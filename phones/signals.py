from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Listing
from core.telegram_bot import send_admin_notification

@receiver(post_save, sender=Listing)
def notify_admin_new_listing(sender, instance, created, **kwargs):
    if created:
        message = (
            f"🚀 <b>Yangi E'lon Qo'shildi!</b>\n\n"
            f"🔹 <b>Sarlavha:</b> {instance.title}\n"
            f"📁 <b>Kategoriya:</b> {instance.category.name if instance.category else 'Nomalum'}\n"
            f"💰 <b>Narxi:</b> {float(instance.price):,.0f} so'm\n"
            f"📍 <b>Manzil:</b> {instance.location}\n"
        )
        if instance.seller_phone:
            message += f"📞 <b>Sotuvchi:</b> {instance.seller_phone}\n"
            
        message += f"\n✅ Tekshiruvdan so'ng saytga chiqadi."
        
        try:
            send_admin_notification(message)
        except Exception:
            pass
