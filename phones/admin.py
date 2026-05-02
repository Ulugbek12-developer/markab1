from django.contrib import admin
from .models import Category, Listing, Favorite

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'location', 'is_booked', 'is_approved', 'created_at')
    list_filter = ('category', 'condition', 'is_booked', 'is_approved', 'location')
    search_fields = ('title', 'description', 'model_name')
    list_editable = ('price', 'is_booked', 'is_approved')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'listing', 'created_at')
