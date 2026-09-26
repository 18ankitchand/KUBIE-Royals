# Aashna Saree & Fashion — Django + DRF migration

This is a newly generated migration project based on the user-provided Netlify source ZIP. The original storefront HTML/CSS/JS, dashboard and six static images are included. Netlify Functions are replaced with Django REST Framework endpoints, PostgreSQL models and Django session authentication. Source data and live Netlify Blobs are **not** in the ZIP and must be exported separately; see `MIGRATION.md`.

## Local setup (PostgreSQL required)

1. Install Python 3.11+ and PostgreSQL. Create an empty database and a least-privilege database user, e.g. `aashna`.
2. `python -m venv .venv`; activate it (`source .venv/bin/activate` on macOS/Linux, `.venv\Scripts\activate` on Windows).
3. `pip install -r requirements.txt`.
4. Set environment variables using `.env.example` as a reference. Django does not auto-load `.env`; if you save your local settings there, run `set -a; source .env; set +a` in each new terminal before running Django commands, or configure your IDE. Set a fresh `DJANGO_SECRET_KEY` and `DJANGO_DEBUG=1` locally. Never commit secrets.
5. `python manage.py migrate`
6. `python manage.py createsuperuser --username shopadmin` (ensure staff privileges).
7. `python manage.py runserver` then open `http://127.0.0.1:8000/` and `http://127.0.0.1:8000/admin/`.
8. `python manage.py test` and `python manage.py check --deploy` (production warnings are expected in local DEBUG mode).

## Production: PythonAnywhere

Confirm your PythonAnywhere account supports your required PostgreSQL access, persistent media and Python version. Create a PythonAnywhere web app using **Manual configuration** with a compatible Python version. Upload/extract this project to `/home/YOUR_USERNAME/aashna`. Create a virtualenv and `pip install -r requirements.txt`. Provision PostgreSQL on an accessible provider and set `DATABASE_URL` (some PythonAnywhere plans restrict outbound database connections; verify before selecting a provider). Set `DJANGO_DEBUG=0`, a unique `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS=YOUR_USERNAME.pythonanywhere.com`, `DJANGO_CSRF_TRUSTED_ORIGINS=https://YOUR_USERNAME.pythonanywhere.com`, and `MEDIA_ROOT=/home/YOUR_USERNAME/aashna_media` in the WSGI environment or a private config mechanism. Do not put passwords in source files.

In the PythonAnywhere Web tab set virtualenv and WSGI app to `config.wsgi.application` (ensure project root is on `sys.path`); configure static mapping `/static/` -> `/home/YOUR_USERNAME/aashna/staticfiles`, media mapping `/media/` -> `/home/YOUR_USERNAME/aashna_media`. Run `python manage.py migrate`, `python manage.py collectstatic --noinput`, create the admin user, verify `python manage.py check --deploy`, reload the web app, then test HTTPS, login, uploads, public pages and images. Enable HTTPS redirects only after proxy HTTPS behavior is verified; set `TRUST_PROXY=1` only if your deployment proxy sets `X-Forwarded-Proto` securely. Configure secure backups and image retention.

## API compatibility

Routes: `GET /api/products[?category=&search=&offers=true&featured=true]`, `GET /api/products/<id>`, `POST /api/products`, `PUT/PATCH/DELETE /api/products/<id>`, `GET/PUT /api/settings`, `GET /api/session`, `POST /api/login`, `POST /api/logout`, `POST /api/upload` (multipart field `image`). Response wrappers and camelCase product fields match the original. Login accepts the password only and authenticates configured `SHOP_ADMIN_USERNAME` (default `shopadmin`) against a Django staff account. CSRF is enforced by Django in a browser; the updated shared.js fetches a CSRF cookie before unsafe requests. The old `shop_admin` cookie is intentionally not accepted.

Django templates serve the preserved frontend; CSS/JS/artwork are moved into Django static files. Netlify's `/.netlify/images` optimization is removed; direct image URLs are used. Configure image optimization/CDN separately if needed. Uploaded image files are never automatically deleted on product changes, preventing accidental loss of shared media; periodically clean orphaned files only after backup and review. Original source is not included in this output ZIP to avoid shipping obsolete insecure backend code.

## Limitations and verification

No live database, secrets, Blob images, or production environment were provided. No live data transfer or production deployment has occurred. The app requires a PostgreSQL service to run tests. Check Django/PythonAnywhere versions and current hosting restrictions before deployment. `MIGRATION.md` describes a cautious cutover and rollback.
