from flask import session, flash, redirect, url_for
# التعديل الجوهري هنا: الاستيراد من models
from models import Vendor

def login_vendor(username, password):
    # الآن سيعمل هذا السطر لأن البرنامج سيعرف مكان Vendor الصحيح
    vendor = Vendor.query.filter_by(username=username).first()
    if vendor and vendor.password == password:
        session['username'] = vendor.username
        session['brand_name'] = vendor.brand_name
        session['wallet'] = vendor.wallet_address
        flash(f"مرحباً بك في نظام {vendor.brand_name}", "success")
        return True
    
    flash("خطأ في بيانات الدخول، تأكد من اسم المستخدم أو كلمة المرور.", "danger")
    return False

def is_logged_in():
    return 'username' in session

def logout():
    session.clear()
    flash("تم تسجيل الخروج بنجاح.", "info")
    return redirect(url_for('login_page'))
