import requests
import io
import json
from PIL import Image

# الإعدادات المحدثة بناءً على صور Sandbox وعنوان الـ API المباشر
GRAPHQL_URL = "https://api.qumra.cloud/graphql"
ACCESS_TOKEN = "qmr_6efc3577-9287-4588-8c87-667e449d5397"

def calculate_final_price(original_price, currency):
    """تحويل العملة وإضافة نسبة الربح 30% لتعزيز نمو منصة محجوب أونلاين"""
    try:
        price = float(original_price)
        # التحويل من دولار إلى ريال سعودي بمعدل ثابت (3.8)
        if str(currency).upper() == 'USD':
            price = price * 3.8
        
        # إضافة هامش الربح 30% والتقريب
        final_price = price * 1.30
        return round(final_price, 2)
    except (ValueError, TypeError):
        return 0.0

def process_product_image(uploaded_file):
    """تحويل ومعالجة الصور إلى WebP لرفع أداء المتجر وتحسين الـ SEO"""
    try:
        img = Image.open(uploaded_file)
        # معالجة القنوات اللونية للصور الشفافة (PNG) لتجنب أخطاء التحويل
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        
        buffer = io.BytesIO()
        # حفظ الصورة بصيغة WebP بجودة 80 توازن بين الحجم والوضوح
        img.save(buffer, format="WebP", quality=80)
        buffer.seek(0)
        return buffer
    except Exception as e:
        print(f"Error processing image (Check if Pillow is installed): {e}")
        return None

def push_to_qmr_store(name, description, final_price, image_buffer):
    """إرسال المنتج كمسودة (Draft) عبر جسر GraphQL إلى متجر قمرة"""
    
    # ترويسات المصادقة (Authorization) كما تم تأكيدها في اختبار Apollo
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Accept": "application/json",
    }

    # الاستعلام (Mutation) المحدث والمطابق لـ Schema قمرة لرفع الملفات
    query = """
    mutation CreateProduct($input: ProductInput!, $image: Upload) {
      createProduct(input: $input, image: $image) {
        id
        name
        status
      }
    }
    """
    
    # تجهيز العمليات (Operations) - تأكدنا من إرسال السعر كـ Float
    operations = {
        'query': query,
        'variables': {
            'input': {
                'name': name,
                'description': description if description else "منتج من منصة محجوب أونلاين",
                'price': float(final_price),
                'status': 'DRAFT',
                'currency': 'SAR'
            },
            'image': None  # يتم ربطه برمجياً عبر الـ Map
        }
    }
    
    # خريطة الربط (Mapping) لرفع الملف
    map_data = {'0': ['variables.image']}
    
    try:
        # بناء الطلب المتعدد (Multipart) لإرسال الصورة والبيانات معاً
        files = {
            'operations': (None, json.dumps(operations), 'application/json'),
            'map': (None, json.dumps(map_data), 'application/json'),
            '0': ('product_image.webp', image_buffer, 'image/webp')
        }
        
        response = requests.post(GRAPHQL_URL, headers=headers, files=files)
        
        # متابعة الحالة في سجلات Railway
        print(f"Qumra Response Status: {response.status_code}")
        
        if response.status_code == 200 and "errors" not in response.text:
            print(f"✅ تم رفع المنتج '{name}' بنجاح.")
            return True
        else:
            # طباعة الخطأ القادم من قمرة في السجلات للتحليل
            print(f"❌ خطأ من API قمرة: {response.text}")
            return False
            
    except Exception as e:
        print(f"⚠️ فشل الاتصال بالجسر التقني: {e}")
        return False
