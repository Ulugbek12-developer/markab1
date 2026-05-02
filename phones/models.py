from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Lucide icon name or Emoji")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class Listing(models.Model):
    CONDITION_CHOICES = [
        ('new', 'Yangi'),
        ('ideal', 'Ideal'),
        ('good', 'Yaxshi'),
        ('bad', 'Ta\'mir talab'),
    ]
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='listings', null=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=15, decimal_places=0)
    
    # Specific attributes (can be JSON or separate fields, keeping it simple for now)
    model_name = models.CharField(max_length=100, blank=True)
    memory = models.CharField(max_length=50, blank=True)
    battery_health = models.IntegerField(null=True, blank=True)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    
    location = models.CharField(max_length=100, default='Toshkent')
    image = models.ImageField(upload_to='listings/', blank=True, null=True)
    images_json = models.JSONField(default=list, blank=True, help_text="Multiple image URLs if any")
    
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings', null=True, blank=True)
    seller_phone = models.CharField(max_length=20, blank=True)
    seller_telegram = models.CharField(max_length=50, blank=True)
    
    is_approved = models.BooleanField(default=True)
    status = models.CharField(max_length=20, default='active') # active, sold, pending
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'listing')
