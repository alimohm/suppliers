from flask import session

def is_admin_logged_in():
    """
    التحقق مما إذا كان المستخدم الحالي هو المدير العام (علي)
    يتم فحص وجود قيمة True للمفتاح 'is_admin' في الجلسة.
    """
    return session.get('is_admin', False)

def verify_admin_credentials(username, password):
    """
    التحقق من بيانات الدخول الإدارية لبرج المراقبة.
    يمكنك تغيير هذه القيم هنا لتحديث بيانات دخولك.
    """
    # بيانات المدير العام للمنصة
    ADMIN_USER = "ali_admin"
    ADMIN_PASS = "Ali_2026_Secure" 
    
    if username == ADMIN_USER and password == ADMIN_PASS:
        return True
    return False

def logout_admin():
    """
    تسجيل الخروج الخاص بالمدير فقط وتطهير الجلسة.
    """
    session.pop('is_admin', None)
    return True
