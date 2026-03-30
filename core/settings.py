import os
import dj_database_url
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# مفتاح الأمان (يفضل وضعه في Variables لاحقاً)
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-your-key-here')

DEBUG = False # اجعلها False عند النشر

ALLOWED_HOSTS = ['*'] # يسمح لـ Railway بالوصول للموقع

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # أضف تطبيقاتك هنا (مثل suppliers)
]

# إعدادات قاعدة البيانات للربط مع Railway
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True
    )
}

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
