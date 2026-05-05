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
    color = models.CharField(max_length=50, blank=True)
    memory = models.CharField(max_length=50, blank=True)
    region = models.CharField(max_length=50, blank=True)
    battery_health = models.IntegerField(null=True, blank=True)
    
    # Detailed Condition
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='ideal') # Legacy fallback
    screen_condition = models.CharField(max_length=50, blank=True)
    body_condition = models.CharField(max_length=50, blank=True)
    
    # Hardware & Documents
    replaced_parts = models.JSONField(default=list, blank=True)
    defects = models.JSONField(default=list, blank=True)
    has_box = models.BooleanField(default=False)
    
    location = models.CharField(max_length=100, default='Toshkent')
    image = models.ImageField(upload_to='listings/', blank=True, null=True)
    images_json = models.JSONField(default=list, blank=True, help_text="Multiple image URLs if any")
    
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings', null=True, blank=True)
    seller_phone = models.CharField(max_length=20, blank=True)
    seller_telegram = models.CharField(max_length=50, blank=True)
    
    is_approved = models.BooleanField(default=True)
    status = models.CharField(max_length=20, default='active') # active, sold, pending
    
    # Booking & Sale system
    is_booked = models.BooleanField(default=False)
    booked_until = models.DateTimeField(null=True, blank=True)
    is_sale = models.BooleanField(default=False, help_text="Aksiya/Chegirma")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

class Branch(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    map_url = models.URLField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return self.name

class Review(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=5, choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.listing.title} ({self.rating})"

    class Meta:
        ordering = ['-created_at']

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'listing')
