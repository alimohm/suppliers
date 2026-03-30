import os
import sys
from pathlib import Path
from django.core.wsgi import get_wsgi_application

# الحصول على المسار المطلق لمجلد المشروع (المجلد الذي يحتوي على core و manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent

# إضافة المسار إلى أول قائمة البحث لضمان الأولوية
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# التأكد من ضبط المتغير البيئي للإعدادات
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

try:
    application = get_wsgi_application()
except Exception as e:
    print(f"Error loading WSGI application: {e}")
    raise
