from flask import session

def is_admin_logged_in():
    """التحقق من جلسة المدير العام (صبري)"""
    return session.get('is_admin', False)

def verify_admin_credentials(username, password):
    """
    التحقق من بيانات دخول برج المراقبة للمدير صبري
    """
    # بيانات الإدارة الجديدة
    ADMIN_USER = "صبري"
    ADMIN_PASS = "123" 
    
    if username == ADMIN_USER and password == ADMIN_PASS:
        return True
    return False

def logout_admin():
    """تسجيل خروج المدير"""
    session.pop('is_admin', None)
    return True
