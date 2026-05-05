from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    USER_ROLE_CHOICES = (
        ('customer', 'Oluvchi/Ko\'ruvchi'),
        ('seller_user', 'Sotuvchi (User)'),
        ('staff_seller', 'Sotuvchi (Admin)'),
        ('staff_cashier', 'Kassir (Admin)'),
        ('head_admin', 'Head Admin (Direktor)'),
    )
    role = models.CharField(max_length=20, choices=USER_ROLE_CHOICES, default='customer')
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def is_head_admin(self):
        return self.role == 'head_admin' or self.is_superuser

    def is_staff_member(self):
        return self.role in ['head_admin', 'staff_seller', 'staff_cashier'] or self.is_staff
