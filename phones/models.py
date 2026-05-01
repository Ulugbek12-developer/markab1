from django.db import models

class Phone(models.Model):
    CONDITION_CHOICES = [
        ('ideal', 'Ideal'),
        ('medium', 'Medium'),
        ('bad', 'Bad'),
    ]
    
    MEMORY_CHOICES = [
        ('64', '64 GB'),
        ('128', '128 GB'),
        ('256', '256 GB'),
        ('512', '512 GB'),
        ('1024', '1 TB'),
    ]
    
    MODEL_CHOICES = [
        ('11', 'iPhone 11'),
        ('11 Pro', 'iPhone 11 Pro'),
        ('11 Pro Max', 'iPhone 11 Pro Max'),
        ('12 Mini', 'iPhone 12 Mini'),
        ('12', 'iPhone 12'),
        ('12 Pro', 'iPhone 12 Pro'),
        ('12 Pro Max', 'iPhone 12 Pro Max'),
        ('13 Mini', 'iPhone 13 Mini'),
        ('13', 'iPhone 13'),
        ('13 Pro', 'iPhone 13 Pro'),
        ('13 Pro Max', 'iPhone 13 Pro Max'),
        ('14', 'iPhone 14'),
        ('14 Plus', 'iPhone 14 Plus'),
        ('14 Pro', 'iPhone 14 Pro'),
        ('14 Pro Max', 'iPhone 14 Pro Max'),
        ('15', 'iPhone 15'),
        ('15 Plus', 'iPhone 15 Plus'),
        ('15 Pro', 'iPhone 15 Pro'),
        ('15 Pro Max', 'iPhone 15 Pro Max'),
        ('16', 'iPhone 16'),
        ('16 Plus', 'iPhone 16 Plus'),
        ('16 Pro', 'iPhone 16 Pro'),
        ('16 Pro Max', 'iPhone 16 Pro Max'),
        ('17', 'iPhone 17'),
        ('17 Pro', 'iPhone 17 Pro'),
        ('17 Pro Max', 'iPhone 17 Pro Max'),
    ]

    model_name = models.CharField(max_length=50, choices=MODEL_CHOICES)
    memory = models.CharField(max_length=10, choices=MEMORY_CHOICES)
    battery_health = models.IntegerField(default=100)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    price = models.DecimalField(max_digits=15, decimal_places=0)
    color = models.CharField(max_length=50, blank=True)
    region = models.CharField(max_length=50, blank=True)
    has_box = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='phones/', blank=True, null=True)
    is_approved = models.BooleanField(default=True)
    seller_phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_model_name_display()} - {self.memory}GB"

    class Meta:
        ordering = ['-created_at']
