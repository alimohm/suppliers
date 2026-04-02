import os
import requests
import json

# الرابط المستخرج من واجهة GraphQL الخاصة بك
GRAPHQL_URL = "https://mahjoub.online/admin/graphql"

# المفتاح الذي أنشأته (Access Token) - تأكد من وضعه في إعدادات Railway
API_KEY = os.environ.get("QUMRA_ACCESS_TOKEN", "ضع_المفتاح_هنا_إذا_لم_تضعه_في_railway")

def send_to_qumra_webhook(name, price, description, image_filename=None):
    """
    إرسال المنتج كمسودة (DRAFT) عبر GraphQL مع معالجة الحروف العربية.
    """
    # رابط سيرفرك في Railway للوصول للصور المرفوعة
    BASE_URL = "https://mahjoub-online-1-production-c824.up.railway.app"
    
    headers = {import os
import requests
import json

# الرابط المستخرج من واجهة GraphQL الخاصة بك
GRAPHQL_URL = "https://mahjoub.online/admin/graphql"

# المفتاح الذي أنشأته (Access Token)
API_KEY = os.environ.get("QUMRA_ACCESS_TOKEN", "ضع_المفتاح_هنا")

def send_to_qumra_webhook(name, price, description, image_filename=None):
    """
    إرسال المنتج كمسودة (DRAFT) عبر GraphQL مع معالجة الحروف العربية.
    """
    # رابط سيرفرك في Railway للوصول للصور المرفوعة
    BASE_URL = "https://mahjoub-online-1-production-c824.up.railway.app"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # بناء الاستعلام (Mutation) المتوافق مع GraphQL
    query = """
    mutation CreateNewProduct($input: CreateProductInput!) {
      createProduct(input: $input) {
        id
        title
        status
      }
    }
    """
    
    # تجهيز البيانات (المتغيرات)
    variables = {
        "input": {
            "title": name,
            "price": float(price),
            "description": description,
            "status": "DRAFT",
            "image": f"{BASE_URL}/static/uploads/{image_filename}" if image_filename else None
        }
    }

    try:
        # تحويل البيانات إلى JSON بتشفير UTF-8 لضمان سلامة اللغة العربية
        data_to_send = json.dumps(
            {'query': query, 'variables': variables}, 
            ensure_ascii=False
        ).encode('utf-8')
        
        print(f"🚀 محاولة مزامنة المنتج: {name}")
        
        # إرسال الطلب للسيرفر
        response = requests.post(
            GRAPHQL_URL, 
            data=data_to_send, 
            headers=headers, 
            timeout=30
        )
        
        # تحليل الرد لكشف الأخطاء (معالجة آمنة للطباعة)
        try:
            response_data = response.json()
            # استخدام + بدلاً من f-string للقيم المعقدة لتجنب أخطاء التنسيق
            print("📡 رد السيرفر التفصيلي: " + json.dumps(response_data, indent=2, ensure_ascii=False))
        except:
            print("📡 الرد ليس بتنسيق JSON: " + response.text)

        # التحقق من النجاح
        if response.status_code == 200:
            if "errors" in response_data:
                print("⚠️ رفض السيرفر الطلب بسبب أخطاء في حقول الـ GraphQL")
                return False
            print("✅ تمت المزامنة بنجاح! المنتج الآن مسودة في قمرة.")
            return True
        else:
            print(f"❌ فشل الاتصال. الكود: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ خطأ تقني غير متوقع: {e}")
        return False
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # بناء الاستعلام (Mutation) المتوافق مع نظام قمرة
    query = """
    mutation CreateNewProduct($input: CreateProductInput!) {
      createProduct(input: $input) {
        id
        title
        status
      }
    }
    """
    
    # تجهيز البيانات (المتغيرات)
    variables = {
        "input": {
            "title": name,
            "price": float(price),
            "description": description,
            "status": "DRAFT",  # يصل كمسودة للمراجعة في قمرة
            "image": f"{BASE_URL}/static/uploads/{image_filename}" if image_filename else None
        }
    }

    try:
        # تحويل البيانات إلى JSON مع تشفير UTF-8 لضمان سلامة الحروف العربية (مثل: هاتف، عطر)
        data_to_send = json.dumps(
            {'query': query, 'variables': variables}, 
            ensure_ascii=False
        ).encode('utf-8')
        
        print(f"🚀 محاولة مزامنة المنتج: {name} (الحالة: مسودة)")
        
        # إرسال الطلب للسيرفر
        response = requests.post(
            GRAPHQL_URL, 
            data=data_to_send, 
            headers=headers, 
            timeout=30
        )
        
        # --- فك شفرة الرد لكشف الأخطاء الصامتة ---
        try:
            response_data = response.json()
            print(f"📡 رد السيرفر التفصيلي: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        except:
            print(f"📡 الرد ليس بتنسيق JSON: {response.text}")

        # التحقق من النجاح التقني والبرمجي (GraphQL Errors)
        if response.status_code == 200:
            if "errors" in response_data:
                print(f"⚠️ رفض السيرفر الطلب بسبب أخطاء في
