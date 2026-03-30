import os
import sys
from pathlib import Path
from django.core.wsgi import get_wsgi_application

# إضافة مسار المشروع لبيئة التشغيل
path_root = Path(__file__).resolve().parent.parent
if str(path_root) not in sys.path:
    sys.path.append(str(path_root))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()
