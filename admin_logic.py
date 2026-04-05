from flask import session
from models import AdminUser

def verify_admin_credentials(u, p):
    """
    التحقق من دخول الإدارة المركزية (السيد علي محجوب).
    المنطق المعتمد:
    1. تنظيف المدخلات (admin_user & admin_pass).
    2. التمييز بين الحساب غير المسجل وخطأ كلمة المرور المركزية.
    """
    
    # تنظيف المدخلات لضمان عدم وجود مسافات تعيق الدخول
    admin_id = u.strip() if u else ""
    password = p.strip() if p else ""

    if not admin_id or not password:
        return False, "يرجى إدخال معرف الإدارة وكلمة المرور لتفعيل الدخول."

    # الخطوة 1: البحث عن المعرف في قاعدة بيانات الإدارة المركزية
    # ملاحظة: يتم البحث عن اسم المستخدم (Ali Mahjoub)
    admin = AdminUser.query.filter_by(username=admin_id).first()
    
    if not admin:
        # الحالة: إذا لم يتم العثور على اسم المستخدم في النظام
        return False, "هذا المعرف غير مسجل في نظام الحوكمة الرقمية."

    # الخطوة 2: فحص كلمة المرور المركزية (بعد التأكد من وجود المعرف)
    if admin.password != password:
        # الحالة: المعرف صحيح ولكن كلمة المرور لا تتطابق
        return False, "كلمة المرور المركزية غير صحيحة. تم رصد محاولة دخول."

    # الخطوة 3: نجاح عملية التحقق وتفعيل الجلسة السيادية لبرج المراقبة
    session.clear() # تأمين الجلسة بمسح البيانات السابقة
    session['admin_id'] = admin.id
    session['role'] = 'super_admin' # منح الصلاحية الكاملة
    session['username'] = admin.username
    
    return True, f"مرحباً بك يا سيد {admin.username}. تم تفعيل صلاحيات برج المراقبة."
