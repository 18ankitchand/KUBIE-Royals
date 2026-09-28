
import os
from pathlib import Path
from urllib.parse import urlparse,unquote
from dotenv import load_dotenv
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY=os.environ.get('DJANGO_SECRET_KEY','development-only-not-for-production')
DEBUG=os.environ.get('DJANGO_DEBUG','0')=='1'
if not DEBUG and SECRET_KEY=='development-only-not-for-production':
 raise RuntimeError('Set DJANGO_SECRET_KEY before running production')
ALLOWED_HOSTS=[x.strip() for x in os.environ.get('DJANGO_ALLOWED_HOSTS','localhost,127.0.0.1').split(',') if x.strip()]


CSRF_TRUSTED_ORIGINS=[x.strip() for x in os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS','').split(',') if x.strip()]
INSTALLED_APPS=['django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','rest_framework','shop']



MIDDLEWARE=['django.middleware.security.SecurityMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware']
ROOT_URLCONF='config.urls'


TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.debug','django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']}}]


WSGI_APPLICATION='config.wsgi.application'
USE_SQLITE = os.environ.get('USE_SQLITE', 'False').lower() == 'true'

if USE_SQLITE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    url=os.environ.get('DATABASE_URL','')
    if url:
        parsed=urlparse(url)
        if parsed.scheme not in ('postgres','postgresql'):
            raise RuntimeError('DATABASE_URL must be PostgreSQL')
        DATABASES={'default':{'ENGINE':'django.db.backends.postgresql','NAME':unquote(parsed.path.lstrip('/')),'USER':unquote(parsed.username or ''),'PASSWORD':unquote(parsed.password or ''),'HOST':parsed.hostname or 'localhost','PORT':parsed.port or '5432','OPTIONS':{'sslmode':os.environ.get('PGSSLMODE','prefer')}}}
    else:
        DATABASES={'default':{'ENGINE':'django.db.backends.postgresql','NAME':os.environ.get('PGDATABASE','aashna'),'USER':os.environ.get('PGUSER','aashna'),'PASSWORD':os.environ.get('PGPASSWORD',''),'HOST':os.environ.get('PGHOST','localhost'),'PORT':os.environ.get('PGPORT','5432')}}

AUTH_PASSWORD_VALIDATORS=[{'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},{'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator'},{'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},{'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'}]
LANGUAGE_CODE='en-us';
TIME_ZONE='Asia/Kathmandu';
USE_TZ=True
STATIC_URL='/static/';
STATIC_ROOT=BASE_DIR/'staticfiles';

MEDIA_URL='/media/';
MEDIA_ROOT=Path(os.environ.get('MEDIA_ROOT',str(BASE_DIR/'media')))



DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
SESSION_COOKIE_HTTPONLY=True;SESSION_COOKIE_SAMESITE='Lax';SESSION_COOKIE_AGE=12*3600
CSRF_COOKIE_SAMESITE='Lax';CSRF_COOKIE_HTTPONLY=False
SESSION_COOKIE_SECURE=not DEBUG;CSRF_COOKIE_SECURE=not DEBUG
SECURE_CONTENT_TYPE_NOSNIFF=True;SECURE_SSL_REDIRECT=os.environ.get('DJANGO_SSL_REDIRECT','0')=='1'
SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO','https') if os.environ.get('TRUST_PROXY','0')=='1' else None
X_FRAME_OPTIONS='DENY'
REST_FRAMEWORK={'DEFAULT_AUTHENTICATION_CLASSES':['rest_framework.authentication.SessionAuthentication'],'DEFAULT_PERMISSION_CLASSES':['rest_framework.permissions.AllowAny']}


MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"