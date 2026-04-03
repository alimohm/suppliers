from flask import session
from werkzeug.security import check_password_hash
from models import Vendor

def login_vendor(username, password):
    """
    التحقق من بيانات دخول الموردين وتأمين الجلسة.
    مطابق لهيكل جدول vendor في قاعدة البيانات.
    """
    # البحث عن المورد باستخدام اسم المستخدم
    vendor = Vendor.query.filter_by(username=username).first()
    
    if vendor and check_password_hash(vendor.password, password):
        # التحقق من أن الحساب نشط (تجنب خطأ نقص العمود في القاعدة)
        # تأكد من تنفيذ ALTER TABLE لإضافة status
        if hasattr(vendor, 'status') and vendor.status != 'active':
            return False, "عذراً، هذا الحساب غير مفعل حالياً."
            
        # إنشاء جلسة دخول نظيفة وآمنة
        session.clear()
        session['user_id'] = vendor.id
        session['username'] = vendor.username
        session['brand_name'] = vendor.brand_name
        session['role'] = 'vendor' # تحديد الرتبة لمنع تداخل الصلاحيات مع الإدارة
        
        return True, f"أهلاً بك في نظام {vendor.brand_name}."
    
    return False, "خطأ في اسم المستخدم أو كلمة المرور."

def is_logged_in():
    """
    التحقق من أن المستخدم الحالي هو مورد وليس مسؤول إدارة.
    """
    return session.get('role') == 'vendor' and 'user_id' in session

def get_current_vendor():
    """
    جلب بيانات المورد الحالي من قاعدة البيانات بناءً على الجلسة.
    """
    if is_logged_in():
        return Vendor.query.get(session.get('user_id'))
    return None
