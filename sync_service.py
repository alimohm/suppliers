import os
import requests
import json

GRAPHQL_URL = "https://mahjoub.online/admin/graphql"
API_KEY = str(os.environ.get("QUMRA_ACCESS_TOKEN", "")).strip()

def send_to_qumra_webhook(name, price, description, image_filename=None):
    # استخدام الرابط المباشر للصورة على سيرفر Railway
    BASE_URL = "https://mahjoub-online-1-production-c824.up.railway.app"
    
    headers = {
        "Authorization": "Bearer " + API_KEY,
        "Content-Type": "application/json"
    }

    # استعلام متوافق مع بنية قمرة التي اكتشفناها
    query = """
    mutation CreateProduct($name: String!, $price: Float!, $description: String, $image: String) {
      createProduct(name: $name, price: $price, description: $description, image: $image) {
        _id
        title
      }
    }
    """
    
    variables = {
        "name": str(name),
        "price": float(price),
        "description": str(description),
        "image": (BASE_URL + "/static/uploads/" + str(image_filename)) if image_filename else None
    }

    try:
        # التشفير بـ UTF-8 لدعم العربية
        json_payload = json.dumps({'query': query, 'variables': variables}, ensure_ascii=False)
        encoded_payload = json_payload.encode('utf-8')
        
        print("🚀 Sending product: " + str(name))
        
        response = requests.post(
            GRAPHQL_URL, 
            data=encoded_payload, 
            headers=headers, 
            timeout=30
        )
        
        response_data = response.json()
        
        # طباعة الرد الكامل لفك اللغز
        print("📡 Qumra Response: " + json.dumps(response_data, ensure_ascii=False))

        if response.status_code == 200 and "errors" not in response_data:
            return True
        return False

    except Exception as e:
        print("❌ Error: " + str(e))
        return False
