from flask import session
from werkzeug.security import check_password_hash
from models import Vendor

def login_vendor(u, p):
    """منطق دخول الموردين - التحقق الصارم من الهوية"""
    # 1. البحث عن المورد في القاعدة
    vendor = Vendor.query.filter_by(username=u).first()
    
    # حالة 1: الحساب غير موجود نهائياً
    if not vendor:
        return False, "عذراً، هذا الحساب غير مسجل في المنصة اللامركزية."
    
    # حالة 2: الحساب موجود، نقوم بفحص كلمة المرور (الهاش)
    if check_password_hash(vendor.password, p):
        # نجاح التحقق - إنشاء الجلسة وتأمينها
        session.clear()
        session
