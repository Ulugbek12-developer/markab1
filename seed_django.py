import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from phones.models import Category

def seed_categories():
    categories = [
        {'name': 'Telefonlar', 'slug': 'phones', 'icon': '📱'},
        {'name': 'Noutbuklar', 'slug': 'laptops', 'icon': '💻'},
        {'name': 'Aksessuarlar', 'slug': 'accessories', 'icon': '🎧'},
        {'name': 'Planshetlar', 'slug': 'tablets', 'icon': '平板'},
        {'name': 'Aqlli soatlar', 'slug': 'watches', 'icon': '⌚'},
    ]
    
    for cat_data in categories:
        Category.objects.get_or_create(slug=cat_data['slug'], defaults=cat_data)
        print(f"Category '{cat_data['name']}' created/exists.")

if __name__ == '__main__':
    seed_categories()
