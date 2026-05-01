from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'customer_phone', 'phone', 'is_installment', 'created_at')
    list_filter = ('is_installment', 'created_at')
    search_fields = ('customer_name', 'customer_phone')
