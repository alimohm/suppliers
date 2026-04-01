import os
import requests

# إعدادات الربط - تسحب من Railway أو تستخدم الافتراضي
API_KEY = os.environ.get("QUMRA_API_KEY", "qmr_e235dd03-f398-473f-aa12-79029f05e147")
STORE_ID = "qmr_e235dd03-f398-473f-aa12-79029f05e147"
API_URL = f"https://api.qumra.cloud/v1/stores/{STORE_ID}/products"

# رابط سيرفرك في Railway (تأكد أن هذا هو الرابط الصحيح لمشروعك)
BASE_URL = "https://mahjoub-online-1-production-c824.up.railway.app"

def send_to_qumra_webhook(name, price, description, image_filename=None):
    """
    إرسال المنتج مع رابط الصورة من مجلد uploads الجديد.
    """
    if not API_KEY:
        print("❌ خطأ: مفتاح الـ API غير متوفر.")
        return False

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "title": name,
        "price": float(price) if price else 0.0,
        "description": description,
        "metadata": {"origin": "Mahjoub Online"}
    }

    # الربط مع مجلد uploads الذي أنشأته توكاً
    if image_filename:
        # هذا الرابط هو ما ستستخدمه قمرة لتحميل الصورة لمتجرك
        payload["main_image"] = f"{BASE_URL}/static/uploads/{image_filename}"

    try:
        # مهلة انتظار كافية لمعالجة البيانات والصور
        response = requests.post(API_URL, json=payload, headers=headers, timeout=25)
        
        print(f"📡 محاولة إرسال المنتج '{name}'...")
        print(f"📡 رد قمرة: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print(f"✅ تمت المزامنة بنجاح مع الصورة.")
            return True
        else:
            print(f"⚠️ فشل الإرسال: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {e}")
        return False
