import requests # تأكد من وجود هذا السطر في أعلى الملف

# ... الكود القديم الموجود مسبقاً يظل كما هو ...

# ==========================================
# إعدادات الربط مع متجر قمرة (الويب هوك)
# ==========================================

STORE_ID = "qmr_e235dd03-f398-473f-aa12-79029f05e147"
# ملاحظة: هذا الرابط يعتمد على توثيق API قمرة لرفع المنتجات
WEBHOOK_URL = f"https://api.qumra.cloud/v1/stores/{STORE_ID}/products"
API_KEY = "ضغ_المفتاح_الخاص_بك_هنا" 

def sync_product_to_qumra(name, price, description, image_url=None):
    """
    دالة إرسال بيانات المنتج إلى متجر قمرة عبر Webhook
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # تجهيز البيانات المرسلة (Payload)
    payload = {
        "title": name,
        "price": float(price),
        "description": description,
        "image": image_url,
        "metadata": {
            "source": "Mahjoub Online",
            "sync_date": "2026-04-01"
        }
    }

    try:
        # إرسال الطلب بنظام POST
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers, timeout=10)
        
        if response.status_code in [200, 201]:
            print(f"✅ تم مزامنة المنتج {name} بنجاح.")
            return True
        else:
            print(f"❌ فشلت المزامنة. كود الخطأ: {response.status_code}")
            print(f"الرد: {response.text}")
            return False
            
    except Exception as e:
        print(f"⚠️ خطأ أثناء الاتصال بسيرفر قمرة: {e}")
        return False

import requests

# بيانات الربط الثابتة
STORE_ID = "qmr_e235dd03-f398-473f-aa12-79029f05e147"
WEBHOOK_URL = f"https://api.qumra.cloud/v1/stores/{STORE_ID}/products"
API_KEY = "ضغ_المفتاح_هنا" 

def handle_product_sync(form_data):
    """دالة معالجة البيانات وإرسال الويب هوك"""
    name = form_data.get('name')
    price = form_data.get('price')
    description = form_data.get('description')

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "title": name,
        "price": float(price) if price else 0,
        "description": description,
        "metadata": {"source": "Mahjoub Online"}
    }

    try:
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers, timeout=10)
        return response.status_code in [200, 201], name
    except:
        return False, name
