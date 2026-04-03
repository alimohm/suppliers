from flask import session
from werkzeug.security import check_password_hash
from models import AdminUser

def verify_admin_credentials(u, p):
    """
    التحقق من صلاحيات الإدارة المركزية (علي محجوب)
    u: اسم المستخدم القادم من الفورم (admin_user)
    p: كلمة المرور القادمة من الفورم (admin_pass)
    """
    
    # 1. التأكد من أن الحقول ليست فارغة
    if not u or not p:
        return False, "يرجى إدخال اسم المستخدم وكلمة المرور للوصول لبرج المراقبة."

    # 2. البحث عن المدير في قاعدة البيانات
    # ملاحظة: يجب أن يتطابق 'u' مع الاسم المحقون 'علي محجوب'
    admin = AdminUser.query.filter_by(username=u).first()
    
    # حالة 1: المعرف غير موجود في السجلات
    if not admin:
        return False, "تنبيه: هذا المعرف غير مسجل ضمن طاقم الإدارة المركزية."
    
    # 3. حالة 2: المعرف موجود، نتحقق من كلمة المرور (الهاش)
    if check_password_hash(admin.password, p):
        # نجاح التحقق - تنظيف الجلسة وإنشاء هوية الإدارة
        session.clear()
        session['admin_id'] = admin.id
        session['role'] = 'admin'
        session['admin_user'] = admin.username
        return True, "تم تأكيد الصلاحيات. مرحباً بك في لوحة التحكم المركزية."
    
    # حالة 3: كلمة المرور لا تطابق الهاش المخزن
    else:
        return False, "خطأ في كلمة المرور: لا تملك صلاحية الوصول لبرج المراقبة."

def is_admin_logged_in():
    """التحقق هل المستخدم الحالي هو مدير مسجل الدخول فعلاً"""
    return session.get('role') == 'admin' and 'admin_id' in session
