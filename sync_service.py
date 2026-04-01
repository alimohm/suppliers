
import requests

# إعدادات الهوية الرقمية للمتجر المستهدف
STORE_ID = "qmr_e235dd03-f398-473f-aa12-79029f05e147"
WEBHOOK_URL = f"https://api.qumra.cloud/v1/stores/{STORE_ID}/products"
API_KEY = "ضغ_المفتاح_الخاص_بك_هنا" 

def send_to_qumra_webhook(name, price, description):
    """
    المحرك المستقل لإرسال البيانات عبر الويب هوك
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "title": name,
        "price": float(price) if price else 0,
        "description": description,
        "metadata": {
            "origin": "Mahjoub Online System",
            "sync_version": "2.0"
        }
    }

    try:
        # تنفيذ عملية المزامنة
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers, timeout=12)
        
        # إرجاع النتيجة (نجاح/فشل)
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"خطأ في محرك المزامنة: {e}")
        return False
