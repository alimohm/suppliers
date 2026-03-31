import requests
import io
import json
from PIL import Image

# 1. الإعدادات السيادية لمنصة محجوب أونلاين
# نستخدم الرابط الخاص بك مباشرة كما يظهر في إعدادات متجرك
GRAPHQL_URL = "https://mahjoub.online/admin/graphql"

# المفتاح السري الخاص بك المستخرج من لوحة التحكم
ACCESS_TOKEN = "qmr_6efc3577-9287-4588-8c87-667e449d5397"

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
        # هذه الدالة تتطلب وجود مكتبة Pillow في requirements.txt
        img = Image.open(uploaded_file)
        
        # التأكد من توافق الألوان عند التحويل من صيغ شفافة مثل PNG
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        
        buffer = io.BytesIO()
        # حفظ الصورة بصيغة WebP المضغوطة بجودة 80
        img.save(buffer, format="WebP", quality=80)
        buffer.seek(0)
        return buffer
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def push_to_qmr_store(name, description, final_price, image_buffer):
    """إرسال بيانات المنتج مباشرة إلى نقطة اتصال mahjoub.online"""
    
    # ترويسات المصادقة باستخدام Bearer Token
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Accept": "application/json",
    }

    # استعلام الـ Mutation المتوافق مع بروتوكول رفع الملفات في GraphQL
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
                'status': 'DRAFT', # يظهر كمسودة للمراجعة أولاً
                'currency': 'SAR'
            },
            'image': None  # سيتم ربطه عبر خريطة الملفات (Map)
        }
    }
    
    # خريطة الربط لإخبار السيرفر بربط الصورة بالمتغير image
    map_data = {'0': ['variables.image']}
    
    try:
        # تشكيل طلب Multipart المخصص لرفع الصور
        files = {
            'operations': (None, json.dumps(operations), 'application/json'),
            'map': (None, json.dumps(map_data), 'application/json'),
            '0': ('product_image.webp', image_buffer, 'image/webp')
        }
        
        # إرسال الطلب الفعلي لنقطة الاتصال الخاصة بك
        response = requests.post(GRAPHQL_URL, headers=headers, files=files)
        
        # طباعة النتيجة في سجلات Railway للمراقبة
        print(f"Server Response Status: {response.status_code}")
        
        if response.status_code == 200 and "errors" not in response.text:
            print(f"✅ تم رفع المنتج '{name}' بنجاح إلى متجر محجوب أونلاين.")
            return True
        else:
            print(f"❌ خطأ في API: {response.text}")
            return False
            
    except Exception as e:
        print(f"⚠️ فشل اتصال الجسر: {e}")
        return False
