import os
import sys
from pathlib import Path
from django.core.wsgi import get_wsgi_application

# الحصول على المسار الرئيسي للمشروع (المجلد الذي يحتوي على manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent

# إضافة المسار الرئيسي لنظام بايثون لكي يرى مجلد core
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# التأكد من توجيه بايثون لملف الإعدادات
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()
