from flask import session, flash, redirect, url_for
from database import db, Vendor

# 1. دالة تسجيل الدخول (يجب أن تكون بنفس الاسم)
def login_vendor(username, password):
    try:
        vendor = Vendor.query.filter_by(username=username).first()
        if not vendor:
            flash("تنبيه: هذه الهوية الرقمية غير مسجلة في نظامنا.", "warning")
            return False
        if vendor.password != password:
            flash("خطأ: كلمة المرور غير مطابقة للمفتاح الخاص.", "danger")
            return False
        
        session['vendor_id'] = vendor.id
        session['username'] = vendor.username
        session['brand_name'] = vendor.brand_name or "محجوب أونلاين"
        session['wallet'] = vendor.wallet_address
        return True
    except Exception as e:
        print(f"Logic Error: {e}")
        flash("عذراً، حدث خطأ في الاتصال بالقاعدة.", "danger")
        return False

# 2. الدالة المفقودة التي سببت الانهيار (logout_vendor)
def logout_vendor():
    session.clear()
    flash("تم تسجيل الخروج بنجاح من نظامك السيادي.", "info")
    return redirect(url_for('login_page'))

# 3. دالة التحقق من حالة الدخول
def is_logged_in():
    return 'vendor_id' in session

# 4. دالة جلب بيانات المورد الحالي
def get_vendor_data():
    if is_logged_in():
        return Vendor.query.get(session['vendor_id'])
    return None
