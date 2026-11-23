"""Apply example offers to selected sample products in all four categories.

Run from the project root after reviewing the proposed discounts:
    python manage.py shell < scripts/apply_sample_offers.py

This file does not create products or change availability, prices, or photos.
It updates only discounts on exact product-name/category matches.
Re-running is safe; missing products are reported.
"""
from django.db import transaction
from shop.models import Product

OFFERS = {
    "Sarees": {
        "Classic Red Banarasi Saree": 15,
        "Emerald Green Silk Saree": 10,
        "Rose Pink Chiffon Saree": 20,
        "Lavender Organza Saree": 12,
        "Maroon Festive Silk Saree": 8,
    },
    "Dresses": {
        "Midnight Blue Maxi Dress": 10,
        "Floral Summer Midi Dress": 15,
        "Classic Black Evening Dress": 12,
        "Rose Pink Wrap Dress": 20,
        "Emerald Party Gown": 8,
    },
    "Kurtis": {
        "White Chikankari Kurti": 10,
        "Rose Embroidered Kurti": 12,
        "Navy Anarkali Kurti": 20,
        "Maroon Festive Kurti": 8,
        "Lavender Panelled Kurti": 15,
    },
    "Lehenga": {
        "Royal Red Bridal Lehenga": 8,
        "Emerald Festive Lehenga": 12,
        "Blush Pink Embroidered Lehenga": 10,
        "Midnight Blue Party Lehenga": 15,
        "Peach Floral Lehenga": 20,
    },
}

updated = 0
missing = []
with transaction.atomic():
    for category_name, offers in OFFERS.items():
        for name, discount in offers.items():
            matched = Product.objects.filter(
                category__name__iexact=category_name,
                name__iexact=name,
            )
            count = matched.update(discount_percent=discount)
            updated += count
            if count == 0:
                missing.append(f"{category_name}: {name}")

print(f"Offer products updated: {updated}")
print(f"Total products on offer: {Product.objects.filter(discount_percent__gt=0).count()}")
if missing:
    print("These entries were not found:")
    for name in missing:
        print(f" - {name}")
