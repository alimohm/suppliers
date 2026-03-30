import os
import sys
from pathlib import Path
from django.core.wsgi import get_wsgi_application

# الحصول على المسار المطلق للمجلد الذي يحتوي على core و manage.py
BASE_DIR = Path(__file__).resolve().parent.parent

# إضافة المسار إلى قائمة sys.path لضمان رؤية المجلدات كـ Modules
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

try:
    application = get_wsgi_application()
except Exception as e:
    # طباعة الخطأ في السجلات (Deploy Logs) لتسهيل تتبعه إذا استمر
    print(f"WSGI Error: {e}")
    raise
