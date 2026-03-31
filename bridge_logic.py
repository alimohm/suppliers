import requests
import json
from config import Config

def push_to_store(data):
    # تجهيز طرد البيانات (Webhook Payload)
    payload = {
        "event": "product.create",
        "data": {
            "name": data['name'],
            "price": data['final_price'],
            "description": data['description'],
            "image_url": data['image_url'], # رابط الصورة المرفوعة
            "vendor_wallet": data['wallet'],
            "status": "draft"
        }
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {Config.WEBHOOK_SECRET}" # استخدام المفتاح الأخير
    }

    try:
        response = requests.post(
            Config.WEBHOOK_URL, 
            json=payload, 
            headers=headers, 
            timeout=15
        )
        return response.status_code in [200, 201, 202]
    except Exception as e:
        print(f"Webhook Error: {str(e)}")
        return False
