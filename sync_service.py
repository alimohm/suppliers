import os
import requests
import json

GRAPHQL_URL = "https://mahjoub.online/admin/graphql"
API_KEY = str(os.environ.get("QUMRA_ACCESS_TOKEN", "")).strip()

def send_to_qumra_webhook(name, price, description, image_filename=None):
    BASE_URL = "https://mahjoub-online-1-production-c824.up.railway.app"
    
    headers = {
        "Authorization": "Bearer " + API_KEY,
        "Content-Type": "application/json"
    }

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
        json_payload = json.dumps({'query': query, 'variables': variables}, ensure_ascii=False)
        encoded_payload = json_payload.encode('utf-8')
        
        print("🚀 Sending product to Qumra: " + str(name))
        
        response = requests.post(
            GRAPHQL_URL, 
            data=encoded_payload, 
            headers=headers, 
            timeout=30
        )
        
        response_data = response.json()
        # أهم سطر: طباعة الرد الكامل لنعرف إذا كان هناك خطأ في الحقول
        print("📡 Qumra Full Response: " + json.dumps(response_data, ensure_ascii=False))

        # التحقق من النجاح
        if response.status_code == 200 and "errors" not in response_data:
            return True
        else:
            print("⚠️ Qumra rejected the product or returned errors.")
            return False

    except Exception as e:
        print("❌ Technical Error: " + str(e))
        return False
