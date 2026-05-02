from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from core.telegram_bot import send_admin_notification

# @receiver(post_save, sender=Order)
# def notify_admin_new_order(sender, instance, created, **kwargs):
#     if created:
#         # Bu signal vaqtincha o'chirildi, chunki views.py dagi xabarnoma mukammalroq ishlaydi.
#         pass
