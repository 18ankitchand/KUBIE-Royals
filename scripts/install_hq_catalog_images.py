"""Preview or install illustrative HQ images for the 48 sample products.

Extract KUBIE_Royals_HQ_48_replacement.zip in the project root first.

Preview:
    python manage.py shell < scripts/install_hq_catalog_images.py

Apply after reviewing hq_manifest.json:
    KUBIE_APPLY_IMAGES=1 python manage.py shell < scripts/install_hq_catalog_images.py

This installer only updates image_key and adds an AI-illustration disclosure.
It keeps original image files for rollback and never changes stock or prices.
"""
import json
import os
from datetime import datetime
from pathlib import Path

from django.core.files.base import File
from django.db import transaction
from shop.models import Product

root = Path.cwd()
manifest_path = root / "hq_manifest.json"
if not manifest_path.is_file():
    raise RuntimeError("Missing hq_manifest.json — extract the HQ ZIP in your project root first")

entries = json.loads(manifest_path.read_text(encoding="utf-8"))
if len(entries) != 48 or len({(e["category"], e["name"]) for e in entries}) != 48:
    raise RuntimeError("HQ manifest must contain 48 distinct category/name pairs")

found = []
issues = []
for entry in entries:
    relative_path = Path(entry["file"])
    if relative_path.is_absolute() or ".." in relative_path.parts or relative_path.parts[0] != "hq_images":
        issues.append("Unsafe image path: " + str(relative_path))
        continue
    image_path = root / relative_path
    if not image_path.is_file():
        issues.append("Image missing: " + str(relative_path))
    products = list(Product.objects.filter(
        category__name__iexact=entry["category"], name__iexact=entry["name"]
    ))
    if len(products) != 1:
        issues.append(f"Expected 1 product, found {len(products)}: {entry['category']} / {entry['name']}")
    else:
        found.append((products[0], entry, image_path))

approximate = [e for e in entries if e.get("match_review_required")]
print(f"Matching catalog products: {len(found)}/48")
print(f"Approximate image matches requiring manual review: {len(approximate)}")
for e in approximate:
    print("  REVIEW:", e["category"], "/", e["name"], "<-", e.get("source", e["file"]))
if issues:
    print("CANCELLED — nothing was changed:")
    for issue in issues:
        print(" -", issue)
elif os.environ.get("KUBIE_APPLY_IMAGES") != "1":
    print("PREVIEW ONLY: no changes applied.")
    print("Review the approximate matches above before applying.")
else:
    backup_path = root / ("kubie_image_backup_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".json")
    backup_path.write_text(json.dumps([
        {"id": p.pk, "name": p.name, "old_image": str(p.image_key or "")}
        for p, _, _ in found
    ], indent=2), encoding="utf-8")
    with transaction.atomic():
        for product, entry, image_path in found:
            with image_path.open("rb") as fp:
                product.image_key.save(f"kubie_hq_{product.pk}_{image_path.name}", File(fp), save=False)
            notice = "Image is AI-generated for illustration; actual product may differ."
            if notice not in (product.description or ""):
                product.description = ((product.description or "").rstrip() + "\n\n" + notice).strip()
            product.save(update_fields=["image_key", "description", "updated_at"])
    print("New HQ sample images installed:", len(found))
    print("Old image references backed up to:", backup_path)
    print("Old image files were retained for rollback.")
