import requests
import io
import json
from PIL import Image

# الإعدادات المحدثة بناءً على اختبارات Apollo Sandbox الناجحة
# تم استخدام الرابط المباشر لتجاوز مشاكل الـ Admin والـ Cookies
GRAPHQL_URL = "https://api.qumra.cloud/graphql"
ACCESS_TOKEN = "qmr_6efc3577-9287-4588-8c87-667e449d5397"

def calculate_final_price(original_price, currency):
    """تحويل العملة وإضافة نسبة الربح 30% (نظام الحوكمة الرقمية)"""
    try:
        price = float(original_price)
        # التحويل من دولار إلى ريال سعودي بمعدل ثابت
        if str(currency).upper() == 'USD':
            price = price * 3.8
        
        # إضافة هامش الربح (30%) والتقريب لخانتبن عشريتين
        final_price = price * 1.30
        return round(final_price, 2)
    except (ValueError, TypeError):
        return 0.0

def process_product_image(uploaded_file):
    """تحويل الصورة المرفوعة إلى تنسيق WebP لضمان سرعة التحميل و SEO المتجر"""
    try:
        img = Image.open(uploaded_file)
        # التأكد من توافق الألوان عند التحويل من PNG أو صيغ شفافة
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        
        buffer = io.BytesIO()
        # حفظ الصورة بصيغة WebP المضغوطة
        img.save(buffer, format="WebP", quality=80)
        buffer.seek(0)
        return buffer
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def push_to_qmr_store(name, description, final_price, image_buffer):
    """إرسال بيانات المنتج كمسودة (Draft) إلى متجر قمرة عبر GraphQL"""
    
    # ترويسات المصادقة كما ظهرت في Apollo Sandbox
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Accept": "application/json",
    }

    # استعلام الـ Mutation المتوافق مع بروتوكول Apollo لرفع الملفات
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
                'description': description or "", # تجنب إرسال None في الوصف
                'price': float(final_price),
                'status': 'DRAFT',
                'currency': 'SAR'
            },
            'image': None  # سيتم استبداله عبر خريطة الملفات (Map)
        }
    }
    
    # خريطة الربط لإخبار خادم قمرة بربط الصورة بالمتغير البرمجي
    map_data = {'0': ['variables.image']}
    
    try:
        # تشكيل طلب Multipart المخصص لرفع الصور في GraphQL
        files = {
            'operations': (None, json.dumps(operations), 'application/json'),
            'map': (None, json.dumps(map_data), 'application/json'),
            '0': ('product_image.webp', image_buffer, 'image/webp')
        }
        
        # إرسال الطلب الفعلي للسيرفر
        response = requests.post(GRAPHQL_URL, headers=headers, files=files)
        
        # تسجيل النتيجة في سجلات ريلوي للمراقبة التقنية
        print(f"Qumra Response Status: {response.status_code}")
        
        if response.status_code == 200 and "errors" not in response.text:
            print("Product successfully pushed to Qumra.")
            return True
        else:
            print(f"Qumra API Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Critical Connection Error: {e}")
        return False
