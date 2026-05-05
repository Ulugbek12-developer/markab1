import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from phones.models import Branch

def seed_branches():
    branches = [
        {
            "name": "Malika",
            "address": "Malika savdo markazi, C-blok, 15-do'kon",
            "phone": "+998 90 123 45 67",
            "map_url": "https://maps.google.com/?q=Malika+Market"
        },
        {
            "name": "Abu Saxiy",
            "address": "Abu Saxiy bozori, 2-qator, 45-do'kon",
            "phone": "+998 91 777 00 00",
            "map_url": "https://maps.google.com/?q=Abu+Saxiy"
        }
    ]
    
    for b in branches:
        obj, created = Branch.objects.get_or_create(name=b['name'], defaults=b)
        if created:
            print(f"Created branch: {b['name']}")
        else:
            print(f"Branch already exists: {b['name']}")

if __name__ == "__main__":
    seed_branches()
