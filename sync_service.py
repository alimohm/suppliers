import os
import requests
import json

GRAPHQL_URL = "https://mahjoub.online/admin/graphql"
API_KEY = os.environ.get("QUMRA_ACCESS_TOKEN", "YOUR_TOKEN")

def send_to_qumra_webhook(name, price, description, image_filename=None):
    BASE_URL = "https://mahjoub-online-1-production-c824.app.railway.app" # رابط سيرفرك
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # الاستعلام مع إضافة حقل الحالة (status)
    query = """
    mutation CreateNewProduct($input: CreateProductInput!) {
      createProduct(input: $input) {
        id
        title
        status
      }
    }
    """
    
    # المتغيرات مع تحديد الحالة كمسودة
    variables = {
        "input": {
            "title": name,
            "price": float(price),
            "description": description,
            "status": "DRAFT",  # إرسال المنتج كمسودة للمراجعة
            "image": f"{BASE_URL}/static/uploads/{image_filename}" if image_filename else None
        }
    }

    try:
        # تشفير UTF-8 لضمان وصول اللغة العربية (هاتف، عطر، إلخ)
        data_to_send = json.dumps({'query': query, 'variables': variables}, ensure_ascii=False).encode('utf-8')
        
        print(f"🚀 جاري إرسال المنتج كمسودة: {name}")
        
        response = requests.post(
            GRAPHQL_URL, 
            data=data_to_send, 
            headers=headers, 
            timeout=30
        )
        
        print(f"📡 رد السيرفر: {response.status_code} - {response.text}")
        
        # نعتبر العملية ناجحة إذا عاد كود 200 ولم توجد أخطاء في GraphQL
        result = response.json()
        return response.status_code == 200 and "errors" not in result

    except Exception as e:
        print(f"❌ فشل المزامنة: {e}")
        return False
