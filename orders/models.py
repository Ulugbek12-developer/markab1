from django.db import models
from phones.models import Listing

class Order(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='orders')
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=20)
    is_installment = models.BooleanField(default=False)
    installment_months = models.IntegerField(null=True, blank=True)
    
    DELIVERY_CHOICES = [
        ('pickup', 'Kelib olib ketish'),
        ('delivery', 'Dastavka'),
    ]
    delivery_type = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default='pickup')
    branch = models.CharField(max_length=100, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"
