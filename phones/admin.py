from django.contrib import admin
from .models import Phone

@admin.register(Phone)
class PhoneAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'memory', 'battery_health', 'price', 'is_approved', 'created_at')
    list_filter = ('model_name', 'condition', 'is_approved')
    search_fields = ('model_name', 'description')
    list_editable = ('price', 'is_approved')
