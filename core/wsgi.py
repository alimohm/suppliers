import os
import sys
from pathlib import Path
from django.core.wsgi import get_wsgi_application

# الحصول على مسار المجلد الرئيسي (الذي يحتوي على manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent
# إضافة المسار إلى نظام بايثون للبحث
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()
