from flask import session
from werkzeug.security import check_password_hash
from models import AdminUser # التأكد من الاستيراد من models وليس app

def verify_admin_credentials(username, password):
    """
    التحقق من بيانات الإدارة (علي محجوب)
    قاعدتنا: ما كُتب عليه admin فهو للإدارة
    """
    # البحث في جدول AdminUser حصراً
    admin = AdminUser.query.filter_by(username=username).first()
    
    if admin and check_password_hash(admin.password, password):
        # تنظيف أي جلسة سابقة لمنع التضارب مع حساب المورد
        session.clear()
        
        # تثبيت بيانات الإدارة في الجلسة
        session['admin_id'] = admin.id
        session['admin_user'] = admin.username
        session['role'] = 'admin' # المفتاح الأساسي للسيادة
        return True, "تم فتح بوابات برج المراقبة بنجاح."
    
    return False, "عذراً، هذه المنطقة مخصصة للإدارة العليا فقط."

def is_admin_logged_in():
    """التحقق من صلاحيات الإدارة الحالية"""
    return session.get('role') == 'admin' and
