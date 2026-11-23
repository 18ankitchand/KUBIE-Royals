# KUBIE-Royals: high-resolution sample catalogue images

The 48-item catalogue is seeded by `scripts/seed_sample_catalog.py`, with 12 each in Sarees, Dresses, Kurtis, and Lehenga. The HQ image package is named `KUBIE_Royals_HQ_48_replacement.zip`.

**Note:** Images are AI-generated illustrations, not verified photos of actual products. Review color, style, and all manifest entries marked `match_review_required` before using them to advertise inventory.

## Deploy on PythonAnywhere

The ZIP is uploaded separately through PythonAnywhere Files to `/home/anki/KUBIE-Royals/`. In a Bash console:

```bash
cd ~/KUBIE-Royals
git pull origin main
unzip -o KUBIE_Royals_HQ_48_replacement.zip
python manage.py shell < scripts/install_hq_catalog_images.py
```

The last command is **preview only**. Verify `Matching catalog products: 48/48`, confirm all image files are present, and inspect the approximate matches before proceeding.

To apply:

```bash
KUBIE_APPLY_IMAGES=1 python manage.py shell < scripts/install_hq_catalog_images.py
```

The installer saves a dated `kubie_image_backup_*.json` in the project directory before changing any image references. It retains old image files for rollback. It changes only the 48 exact-name sample products and adds an illustration disclosure to their descriptions. It does not remove product records, adjust prices, discounts, or availability.

After applying, reload the application in the PythonAnywhere **Web** tab and verify `https://anki.pythonanywhere.com/`. The installer writes product media under Django's configured `MEDIA_ROOT`; `collectstatic` does not install media images.

## GitHub repository and production media

The code changes and installer are maintained in GitHub. The uploaded ZIP and the database/media files on PythonAnywhere are separate from GitHub. GitHub updates do not themselves update production database image references.

For a source-controlled copy of the approved illustrative image assets, extract the ZIP, inspect the manifest and pictures, and commit `hq_images/` and `hq_manifest.json` from an authenticated Git checkout if you want the images stored in the repository. Do **not** commit `.env`, `db.sqlite3`, `media/`, backups, or credentials. Image asset Git commits may increase repository size.

To see whether files are tracked:

```bash
git status --short
git ls-files hq_images | wc -l
```

## Backups

Keep `kubie_image_backup_*.json` and the previous media directory until new images work. Never permanently delete old media based on ZIP extraction alone.
