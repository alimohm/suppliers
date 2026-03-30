import os

# السماح لجميع الروابط بالوصول
ALLOWED_HOSTS = ['*']

# إعدادات الملفات الساكنة (ضروري جداً لظهور الألوان والستايل)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
