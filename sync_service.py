import os
import requests
import json

# الرابط المستخرج من واجهة GraphQL الخاصة بك في قمرة
GRAPHQL_URL = "https://mahjoub.online/admin/graphql"

# المفتاح الذي أنشأته (Access Token)
# ملاحظة: سيقوم الكود بجلب المفتاح من إعدادات Railway، وإذا لم يجده سيستخدم القيمة الافتراضية
API_KEY = os.environ.get("QUMRA_ACCESS_TOKEN", "ضع_المفتاح_هنا_إذا_لم_تضعه_في_railway")

def send_to_qumra_webhook(name, price, description, image_filename=None):
    """
    إرسال المنتج كمسودة (DRAFT) عبر GraphQL مع معالجة الحروف العربية (UTF-8).
    """
    # رابط سيرفرك في Railway للوصول للصور المرفوعة
    BASE_URL = "https://mahjoub-online-1-production-c824.up.railway.app"
    
    headers = {
        "Authorization": "Bearer " + str(API_KEY),
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
            "image": (BASE_URL + "/static/uploads/" + image_filename) if image_filename else None
        }
    }

    try:
        # تحويل البيانات إلى JSON بتشفير UTF-8 لضمان سلامة اللغة العربية
        data_to_send = json.dumps(
            {'query': query, 'variables': variables}, 
            ensure_ascii=False
        ).encode('utf-8')
        
        print("🚀 محاولة مزامنة المنتج: " + str(name))
        
        # إرسال الطلب للسيرفر
        response = requests.post(
            GRAPHQL_URL, 
            data=data_to_send, 
            headers=headers, 
            timeout=30
        )
        
        # تحليل الرد لكشف الأخطاء (معالجة آمنة للطباعة لتجنب الـ Crash)
        response_data = {}
        try:
            response_data = response.json()
            # طباعة الرد بشكل واضح في الـ Logs
            print("📡 رد السيرفر التفصيلي: " + json.dumps(response_data, indent=2, ensure_ascii=False))
        except:
            print("📡 الرد ليس بتنسيق JSON: " + str(response.text))

        # التحقق من النجاح التقني والبرمجي
        if response.status_code == 200:
            if "errors" in response_data:
                print("⚠️ رفض السيرفر الطلب بسبب أخطاء في حقول الـ GraphQL")
                return False
            print("✅ تمت المزامنة بنجاح! المنتج الآن مسودة في قمرة.")
            return True
        else:
            print("❌ فشل الاتصال. الكود: " + str(response.status_code))
            return False

    except Exception as e:
        print("❌ خطأ تقني غير متوقع: " + str(e))
        return False
