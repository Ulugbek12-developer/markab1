import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from phones.models import Phone

def create_sample_data():
    # Clear existing data
    Phone.objects.all().delete()
    
    phones = [
        {
            'model_name': '13 Pro',
            'memory': '128',
            'battery_health': 88,
            'condition': 'ideal',
            'price': 7200000,
            'region': 'LL/A',
            'has_box': True,
            'image': 'phones/13pro.png',
            'description': 'Ideal holatda, aybi yoq. Karobka dokument bor. Rangi Sierra Blue.',
            'seller_phone': '+998901234567'
        },
        {
            'model_name': '14 Pro Max',
            'memory': '256',
            'battery_health': 92,
            'condition': 'ideal',
            'price': 12500000,
            'region': 'KH/A',
            'has_box': True,
            'image': 'phones/14promax.png',
            'description': 'Deep Purple rangi, yangidek turibdi. Hamma narsasi bor.',
            'seller_phone': '+998939876543'
        },
        {
            'model_name': '15 Pro',
            'memory': '128',
            'battery_health': 100,
            'condition': 'ideal',
            'price': 13800000,
            'region': 'LL/A',
            'has_box': True,
            'image': 'phones/15pro.png',
            'description': 'Natural Titanium rangi. Yangi, karobkadan chiqmagan.',
            'seller_phone': '+998944445566'
        },
        {
            'model_name': '12',
            'memory': '128',
            'battery_health': 82,
            'condition': 'medium',
            'price': 4800000,
            'region': 'CH/A',
            'has_box': False,
            'description': 'Oq rangli. Ekranda kichik qirilgan joyi bor. Ishlashi zo\'r.',
            'seller_phone': '+998991112233'
        }
    ]

    for p in phones:
        Phone.objects.create(**p)
    
    print("Sample data created successfully!")

if __name__ == "__main__":
    create_sample_data()
