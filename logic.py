# ملف المنطق: logic.py
# انتبه: لا تقم باستيراد db هنا لمنع التعليق
from database import Vendor

def do_auth(u, p):
    """
    وظيفة التحقق من الهوية من قاعدة البيانات مباشرة
    """
    try:
        # البحث عن المستخدم في جدول الموردين
        user = Vendor.query.filter_by(username=u).first()
        
        # 1. التحقق من وجود المستخدم
        if not user:
            return {
                "status": False, 
                "msg": "اسم المستخدم غير مسجل في المنصة اللامركزية"
            }
        
        # 2. التحقق من تطابق كلمة المرور
        if user.password != p:
            return {
                "status": False, 
                "msg": "كلمة المرور غير صحيحة، يرجى المحاولة مرة أخرى"
            }
        
        # 3. نجاح التحقق وإعادة بيانات الهوية كاملة
        return {
            "status": True, 
            "user": user
        }
        
    except Exception as e:
        # معالجة أي خطأ مفاجئ في الاتصال بالقاعدة
        return {
            "status": False, 
            "msg": f"خطأ في الاتصال بقاعدة البيانات: {str(e)}"
        }
