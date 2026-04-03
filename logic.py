from flask import session
from werkzeug.security import check_password_hash
from models import Vendor

def login_vendor(username, password):
    """منطق دخول الموردين مع رسائل خطأ دقيقة"""
    # البحث عن المورد
    vendor = Vendor.query.filter_by(username=username).first()
    
    # 1. إذا كان المستخدم غير موجود أصلاً
    if not vendor:
        return False, "عذراً، هذا الحساب غير مسجل في المنصة اللامركزية (محجوب أونلاين)."
    
    # 2. إذا وجد المستخدم ولكن كلمة المرور خطأ
    if not check_password_hash(vendor.password, password):
        return False, "كلمة المرور غير صحيحة، يرجى التأكد من مفاتيح الدخول الخاصة بك."
    
    # 3. إذا كان الحساب غير نشط (اختياري)
    if hasattr(vendor, 'status') and vendor.status != 'active':
        return False, "هذا الحساب معلق حالياً في الشبكة."

    # نجاح الدخول
    session.clear()
    session['user_id'] = vendor.id
    session['role'] = 'vendor'
    session['username'] = vendor.username
    return True, f"تم الاتصال بنجاح. أهلاً بك يا {vendor.brand_name}."

def is_logged_in():
    return session.get('role') == 'vendor' and 'user_id' in session
