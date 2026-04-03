from flask import session
from werkzeug.security import check_password_hash
from models import AdminUser

def verify_admin_credentials(u, p):
    if not u or not p:
        return False, "يرجى إدخال كافة البيانات."
    
    admin = AdminUser.query.filter_by(username=u).first()
    if not admin:
        return False, "تنبيه: هذا المعرف غير مسجل في الإدارة المركزية."
    
    # التأكد من مطابقة الهاش
    if check_password_hash(admin.password, p):
        session.clear()
        session['admin_id'] = admin.id
        session['role'] = 'admin'
        return True, "تم تأكيد الصلاحيات."
    
    return False, "خطأ في كلمة المرور: لا تملك صلاحية الوصول."
