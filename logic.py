from flask import session, flash, redirect, url_for
from database import db, Vendor

def login_vendor(username, password):
    """
    التحقق من الهوية الرقمية في النظام اللامركزي
    """
    try:
        # 1. البحث عن الهوية (Username) في القاعدة
        vendor = Vendor.query.filter_by(username=username).first()
        
        # الحالة الأولى: الهوية غير موجودة تماماً
        if not vendor:
            flash("تنبيه: هذه الهوية الرقمية غير مسجلة في النظام اللامركزي.", "warning")
            return False
            
        # الحالة الثانية: الهوية موجودة لكن كلمة المرور خاطئة
        if vendor.password != password:
            flash("خطأ: كلمة المرور غير مطابقة للمفتاح الخاص بهذه الهوية.", "danger")
            return False
            
        # الحالة الثالثة: نجاح التحقق - استخراج البيانات السيادية
        session['vendor_id'] = vendor.id
        session['username'] = vendor.username
        session['brand_name'] = vendor.brand_name or f"متجر {vendor.username}"
        session['wallet'] = vendor.wallet_address # محفظة MAH
        
        flash(f"تم التحقق من الهوية بنجاح. أهلاً بك في سوقك الذكي.", "success")
        return True
            
    except Exception as e:
        print(f"Logic Error: {e}")
        flash("عذراً، حدث خطأ في الاتصال بالعقدة المركزية للقاعدة.", "danger")
        return False
