import os
from pathlib import Path
import dj_database_url  # لربط قاعدة بيانات Postgres تلقائياً

# ... (الإعدادات الافتراضية)

# أهم سطر ليفتح الرابط في المتصفح
ALLOWED_HOSTS = ['*']  # مؤقتاً للسماح بجميع الروابط، أو ضع رابط Railway الخاص بك

# إعدادات قاعدة البيانات من Railway
DATABASES = {
    'default': dj_database_url.config(default=os.environ.get('DATABASE_URL'))
}

# إعدادات الملفات الساكنة (Static Files) لتظهر الواجهة بشكل صحيح
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
