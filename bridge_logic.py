import requests
import io
import json
from PIL import Image

# 1. الإعدادات السيادية لمنصة محجوب أونلاين
# نقطة الاتصال الخاصة بمتجرك مباشرة
GRAPHQL_URL = "https://mahjoub.online/admin/graphql"

# المفتاح الجديد ذو الصلاحيات الكاملة (Write/Read)
ACCESS_TOKEN = "qmr_e235dd03-f398-473f-aa12-79029f05e147"

def calculate_final_price(original_price, currency):
    """تحويل العملة وإضافة نسبة الربح 30% (نظام الحوكمة الرقمية)"""
    try:
        price = float(original_price)
        # التحويل من دولار إلى ريال سعودي بمعدل ثابت 3.8
        if str(currency).upper() == 'USD':
            price = price * 3.8
        
        # إضافة هامش الربح (30%) والتقريب لخانتبن عشريتين
        final_price = price * 1.30
        return round(final_price, 2)
    except (ValueError, TypeError):
        return 0.0

def process_product_image(uploaded_file):
    """تحويل الصورة إلى WebP لضمان أعلى سرعة وتحسين SEO المتجر"""
    try:
        # ملاحظة: تتطلب مكتبة Pillow في ملف requirements.txt
        img = Image.open(uploaded_file)
        
        # التأكد من توافق الألوان عند التحويل من صيغ شفافة مثل PNG
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        
        buffer = io.BytesIO()
        # حفظ الصورة بصيغة WebP المضغوطة لرفع أداء المتجر
        img.save(buffer, format="WebP", quality=80)
        buffer.seek(0)
        return buffer
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def push_to_qmr_store(name, description, final_price, image_buffer):
    """إرسال بيانات المنتج مباشرة إلى نقطة اتصال mahjoub.online"""
    
    # ترويسات المصادقة باستخدام Bearer Token الجديد
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Accept": "application/json",
    }

    # استعلام الـ Mutation المعتمد لرفع المنتجات في قمرة
    query = """
    mutation CreateProduct($input: ProductInput!, $image: Upload) {
      createProduct(input: $input, image: $image) {
        id
        name
        status
      }
    }
    """
    
    # تجهيز كائن العمليات (Operations)
    operations = {
        'query': query,
        'variables': {
            'input': {
                'name': name,
                'description': description or "منتج من منصة محجوب أونلاين",
                'price': float(final_price),
                'status': 'DRAFT', # يظهر كمسودة للمراجعة والتدقيق
                'currency': 'SAR'
            },
            'image': None  # يتم ربطه عبر خريطة الملفات (Map)
        }
    }
    
    # خريطة الربط (Mapping) لرفع الملف البرمجي
    map_data = {'0': ['variables.image']}
    
    try:
        # تشكيل طلب Multipart المخصص لرفع الصور والبيانات
        files = {
            'operations': (None, json.dumps(operations), 'application/json'),
            'map': (None, json.dumps(map_data), 'application/json'),
            '0': ('product_image.webp', image_buffer, 'image/webp')
        }
        
        # إرسال الطلب الفعلي لنقطة الاتصال السيادية
        response = requests.post(GRAPHQL_URL, headers=headers, files=files)
        
        # طباعة النتيجة في سجلات Railway للمراقبة
        print(f"Server Response Status: {response.status_code}")
        
        if response.status_code == 200 and "errors" not in response.text:
            print(f"✅ نجاح: تم دفع المنتج '{name}' إلى المتجر بنجاح.")
            return True
        else:
            print(f"❌ فشل: رد السيرفر يحتوي على أخطاء: {response.text}")
            return False
            
    except Exception as e:
        print(f"⚠️ خطأ فادح في اتصال الجسر: {e}")
        return False
