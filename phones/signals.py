from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Phone
from core.telegram_bot import send_admin_notification

@receiver(post_save, sender=Phone)
def notify_admin_new_phone(sender, instance, created, **kwargs):
    if created:
        message = (
            f"📱 <b>Yangi Mahsulot Qo'shildi!</b>\n\n"
            f"🔹 <b>Model:</b> {instance.get_model_name_display()}\n"
            f"🏢 <b>Filial:</b> {instance.get_branch_display()}\n"
            f"💾 <b>Xotira:</b> {instance.memory} GB\n"
            f"🔋 <b>Batareya:</b> {instance.battery_health}%\n"
            f"🎨 <b>Rangi:</b> {instance.color}\n"
            f"💰 <b>Narxi:</b> {float(instance.price):,.0f} so'm\n"
            f"📝 <b>Holati:</b> {instance.get_condition_display()}\n"
        )
        if instance.seller_phone:
            message += f"📞 <b>Sotuvchi:</b> {instance.seller_phone}\n"
            
        message += f"\n✅ Mahsulot saytga muvaffaqiyatli joylandi."
        
        send_admin_notification(message)

        # Sync to Bot DB (smart_market.db)
        import sqlite3
        from core.settings import BASE_DIR
        import os
        db_path = os.path.join(BASE_DIR.parent, 'smart_market.db')
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ads (user_id, brand, model, photos, battery, storage, condition, region, box, price, contact, branch, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                0, # Admin ID placeholder
                'iPhone',
                instance.get_model_name_display(),
                '', # No photo sync yet or handle properly
                str(instance.battery_health),
                str(instance.memory),
                'ideal' if instance.condition == 'yangi' else 'yaxshi',
                'Toshkent', # Default
                'Bor', # Default
                int(instance.price),
                instance.seller_phone or '',
                'Asosiy', # Default branch
                'approved'
            ))
            conn.commit()
            conn.close()
            with open('sync_debug.log', 'a') as f: f.write("DEBUG: Sync WebApp -> Bot DB success!\n")
        except Exception as e:
            import traceback
            err_msg = f"DEBUG: Sync WebApp -> Bot DB error: {e}\n{traceback.format_exc()}\n"
            with open('sync_debug.log', 'a') as f: f.write(err_msg)
