from flask import session, flash, redirect, url_for
from database import db, Vendor

def login_vendor(username, password):
    try:
        vendor = Vendor.query.filter_by(username=username).first()
        
        if not vendor:
            # هذه الرسالة ستظهر في المربع الأحمر عندك
            flash("تنبيه: هذه الهوية الرقمية غير مسجلة في نظامنا.", "warning")
            return False
            
        if vendor.password != password:
            flash("خطأ: كلمة المرور غير مطابقة للمفتاح الخاص.", "danger")
            return False
            
        # نجاح الدخول
        session['vendor_id'] = vendor.id
        return True
    except Exception as e:
        flash("عذراً، حدث خطأ في الاتصال بالقاعدة.", "danger")
        return False
