import os
import requests

# سحب البيانات من "متغيرات البيئة" في Railway لضمان الأمان والسيادة الرقمية
# سيقرأ الكود هذه القيم من لوحة تحكم Railway مباشرة
API_KEY = os.environ.get("QUMRA_API_KEY", "qmr_e235dd03-f398-473f-aa12-79029f05e147")
API_URL = os.environ.get("QUMRA_API_URL", "https://api.qumra.cloud/v1/products")

def send_to_qumra_webhook(name, price, description):
    """
    وظيفة المزامنة: إرسال بيانات المنتج من لوحة محجوب إلى منصة قمرة.
    """
    
    # التأكد من وجود المفاتيح قبل بدء الاتصال
    if not API_KEY:
        print("❌ خطأ: مفتاح الـ API (QUMRA_API_KEY) غير موجود في متغيرات البيئة!")
        return False

    # إعدادات المصادقة (Headers)
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # تجهيز طرد البيانات (Payload) ليناسب نظام قمرة
    payload = {
        "title": name,
        "price": float(price) if price else 0.0,
        "description": description,
        "metadata": {
            "origin": "Mahjoub Online",
            "platform": "Smart Market",
            "sync_version": "2.0"
        }
    }

    try:
        # إرسال الطلب مع مهلة انتظار 10 ثوانٍ لضمان استقرار السيرفر
        response = requests.post(API_URL, json=payload, headers=headers, timeout=10)
        
        # طباعة النتيجة في سجلات (Logs) Railway للمراقبة الفورية
        print(f"📡 حالة إرسال قمرة: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print(f"✅ تم مزامنة المنتج '{name}' بنجاح.")
            return True
        else:
            print(f"⚠️ قمرة رفضت الطلب. الكود: {response.status_code} - الرد: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏳ خطأ: انتهت مهلة الانتظار أثناء الاتصال بقمرة.")
        return False
    except Exception as e:
        print(f"❌ فشل الاتصال التقني بقمرة: {e}")
        return False
