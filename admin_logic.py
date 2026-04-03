from flask import session, flash

# استيراد AdminUser من الموديلات
# ملاحظة: إذا كان هناك خطأ "Circular Import"، استوردها داخل الدالة
from models import AdminUser 

def verify_admin_credentials(username, password):
    """
    التحقق من بيانات الإدارة المركزية (برج المراقبة)
    """
    # 1. جلب المدير من قاعدة البيانات
    admin = AdminUser.query.filter_by(username=username).first()
    
    # 2. التحقق من وجود المستخدم
    if not admin:
        flash("🚫 هذا المستخدم غير مسجل في المنصة اللامركزية لـ محجوب أونلاين.", "warning")
        return False
    
    # 3. التحقق من مطابقة كلمة المرور
    if admin.password != password:
        flash("⚠️ كلمة المرور غير صحيحة، يرجى التأكد والمحاولة مرة أخرى كمدير.", "danger")
        return False

    # 4. تفعيل الجلسة
    session['is_admin'] = True
    session['admin_user'] = admin.username
    
    flash(f"🛡️ تم تفعيل برج المراقبة بنجاح. مرحباً بك يا سيد {admin.username}", "success")
    return True

def is_admin_logged_in():
    """التحقق من حالة جلسة الإدارة"""
    return session.get('is_admin', False)

def logout_admin_logic():
    """تطهير بيانات الجلسة فقط"""
    session.pop('is_admin', None)
    session.pop('admin_user', None)
    flash("🔒 تم الخروج من برج المراقبة وتأمين النظام بنجاح.", "info")
    return True
