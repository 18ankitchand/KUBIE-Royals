"""Import trusted JSON exports into the NEW database. Never connect to production source here.
Usage: python manage.py shell < scripts/import_exported_data.py
Requires export/products.json and export/settings.json produced by your DBA.
"""
import json
from pathlib import Path
from django.db import transaction,connection
from shop.models import Product,ShopSetting
base=Path('export')
if not (base/'products.json').exists() or not (base/'settings.json').exists():raise RuntimeError('Missing export/products.json or export/settings.json; see MIGRATION.md')
products=json.loads((base/'products.json').read_text());settings=json.loads((base/'settings.json').read_text())
if Product.objects.exists() or ShopSetting.objects.exists():raise RuntimeError('Destination tables must be empty to prevent accidental overwrite')
with transaction.atomic():
 for row in products:
  Product.objects.create(id=row['id'],name=row['name'],category=row['category'],description=row['description'],original_price=row['original_price'],discount_percent=row['discount_percent'],image_key=row['image_key'],fabric=row['fabric'],in_stock=row['in_stock'],featured=row['featured'],created_at=row['created_at'],updated_at=row['updated_at'])
  Product.objects.filter(pk=row['id']).update(created_at=row['created_at'],updated_at=row['updated_at'])
 for row in settings:ShopSetting.objects.create(key=row['key'],value=row['value'])
 with connection.cursor() as cur:cur.execute("SELECT setval(pg_get_serial_sequence('shop_products','id'), COALESCE((SELECT MAX(id) FROM shop_products), 1), (SELECT COUNT(*) > 0 FROM shop_products))")
print('Imported',len(products),'products and',len(settings),'settings. Verify media files separately.')
