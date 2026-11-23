"""Optional sample catalogue. Run only after reviewing demo prices and availability.

Usage: python manage.py shell < scripts/seed_sample_catalog.py
Creates up to 12 sample products in each of the four storefront categories.
Existing products with matching category/name are never modified.
All new samples start out of stock, with no product photo, until verified by the shop.
"""
from django.db import transaction
from shop.models import Category, Product

SAMPLE_CATALOG = {
  "Sarees": [
    [
      "Classic Red Banarasi Saree",
      4200,
      "Silk"
    ],
    [
      "Emerald Green Silk Saree",
      3850,
      "Silk"
    ],
    [
      "Royal Blue Georgette Saree",
      2900,
      "Georgette"
    ],
    [
      "Ivory Cotton Daily Saree",
      1800,
      "Cotton"
    ],
    [
      "Wine Embroidered Party Saree",
      4550,
      "Georgette"
    ],
    [
      "Mustard Yellow Linen Saree",
      2250,
      "Linen"
    ],
    [
      "Rose Pink Chiffon Saree",
      2650,
      "Chiffon"
    ],
    [
      "Black Golden Border Saree",
      3500,
      "Silk blend"
    ],
    [
      "Lavender Organza Saree",
      3900,
      "Organza"
    ],
    [
      "Teal Printed Cotton Saree",
      1950,
      "Cotton"
    ],
    [
      "Maroon Festive Silk Saree",
      4400,
      "Silk"
    ],
    [
      "Peach Floral Saree",
      2450,
      "Georgette"
    ]
  ],
  "Dresses": [
    [
      "Midnight Blue Maxi Dress",
      2850,
      "Polyester blend"
    ],
    [
      "Floral Summer Midi Dress",
      1950,
      "Cotton"
    ],
    [
      "Classic Black Evening Dress",
      3650,
      "Crepe"
    ],
    [
      "Rose Pink Wrap Dress",
      2450,
      "Rayon"
    ],
    [
      "Emerald Party Gown",
      5250,
      "Satin"
    ],
    [
      "Ivory A-Line Dress",
      2350,
      "Cotton blend"
    ],
    [
      "Wine Pleated Midi Dress",
      2950,
      "Georgette"
    ],
    [
      "Sky Blue Casual Dress",
      1750,
      "Cotton"
    ],
    [
      "Lavender Occasion Dress",
      3250,
      "Chiffon"
    ],
    [
      "Mustard Shirt Dress",
      2250,
      "Linen blend"
    ],
    [
      "Navy Printed Maxi Dress",
      2750,
      "Rayon"
    ],
    [
      "Champagne Festive Gown",
      5750,
      "Satin"
    ]
  ],
  "Kurtis": [
    [
      "White Chikankari Kurti",
      2450,
      "Cotton"
    ],
    [
      "Teal Straight-Cut Kurti",
      1750,
      "Rayon"
    ],
    [
      "Mustard Printed Kurti",
      1650,
      "Cotton"
    ],
    [
      "Rose Embroidered Kurti",
      2250,
      "Cotton blend"
    ],
    [
      "Navy Anarkali Kurti",
      2850,
      "Rayon"
    ],
    [
      "Mint Green Daily Kurti",
      1550,
      "Cotton"
    ],
    [
      "Maroon Festive Kurti",
      2650,
      "Silk blend"
    ],
    [
      "Black A-Line Kurti",
      1950,
      "Rayon"
    ],
    [
      "Peach Floral Kurti",
      1750,
      "Cotton"
    ],
    [
      "Lavender Panelled Kurti",
      2150,
      "Viscose"
    ],
    [
      "Olive Green Kurti",
      1850,
      "Linen blend"
    ],
    [
      "Ivory Gold Detail Kurti",
      2750,
      "Silk blend"
    ]
  ],
  "Lehenga": [
    [
      "Royal Red Bridal Lehenga",
      14500,
      "Velvet"
    ],
    [
      "Emerald Festive Lehenga",
      9900,
      "Silk blend"
    ],
    [
      "Blush Pink Embroidered Lehenga",
      11200,
      "Net"
    ],
    [
      "Midnight Blue Party Lehenga",
      8500,
      "Georgette"
    ],
    [
      "Ivory Gold Occasion Lehenga",
      12900,
      "Silk blend"
    ],
    [
      "Wine Velvet Lehenga",
      11800,
      "Velvet"
    ],
    [
      "Peach Floral Lehenga",
      7900,
      "Organza"
    ],
    [
      "Teal Mirrorwork Lehenga",
      9400,
      "Georgette"
    ],
    [
      "Lavender Festive Lehenga",
      8750,
      "Net"
    ],
    [
      "Mustard Mehendi Lehenga",
      8200,
      "Cotton silk"
    ],
    [
      "Champagne Reception Lehenga",
      13800,
      "Satin"
    ],
    [
      "Maroon Zari Lehenga",
      10900,
      "Silk blend"
    ]
  ]
}

created = 0
skipped = 0
with transaction.atomic():
    for category_name, products in SAMPLE_CATALOG.items():
        category, _ = Category.objects.get_or_create(name=category_name)
        for name, sample_price_npr, fabric in products:
            if Product.objects.filter(category=category, name__iexact=name).exists():
                skipped += 1
                continue
            Product.objects.create(
                name=name,
                category=category,
                description=(
                    "Sample catalogue listing for layout preview only. "
                    "Confirm fabric, exact price, photos and availability before selling."
                ),
                original_price=sample_price_npr,
                discount_percent=0,
                fabric=fabric,
                in_stock=False,
                featured=False,
            )
            created += 1
print(f"Sample catalogue: {created} created, {skipped} already present; existing products preserved.")
