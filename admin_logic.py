from flask import session
from models import AdminUser  # استيراد جدول المدير من ملف الموديلات

def is_admin_logged_in():
    """
    التحقق مما إذا كان المدير (صبري) قد سجل دخوله بنجاح.
    نستخدم مفتاح 'is_admin' في الجلسة (Session).
    """
    return session.get('is_admin', False)

def verify_admin_credentials(username, password):
    """
    التحقق من بيانات الدخول من قاعدة البيانات مباشرة.
    تبحث الدالة عن مستخدم في جدول AdminUser يطابق الاسم وكلمة المرور.
    """
    try:
        # البحث عن المدير في قاعدة البيانات (مثلاً: صبري)
        admin = AdminUser.query.filter_by(username=username).first()
        
        # التأكد من مطابقة اسم المستخدم وكلمة المرور
        if admin and admin.password == password:
            return True
        return False
    except Exception as e:
        print(f"❌ خطأ في الاتصال بقاعدة البيانات أثناء التحقق: {e}")
        return False

def logout_admin():
    """
    إنهاء جلسة المدير وتطهير بيانات الدخول من المتصفح.
    """
    session.pop('is_admin', None)
    session.pop('admin_user', None)
    return True
