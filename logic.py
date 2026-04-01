from flask import session, flash, redirect, url_for
from database import db, Vendor

def login_vendor(username, password):
    """التحقق الذكي من الهوية في النظام اللامركزي"""
    try:
        vendor = Vendor.query.filter_by(username=username).first()
        if not vendor:
            flash("تنبيه: هذه الهوية الرقمية غير مسجلة في النظام.", "warning")
            return False
        if vendor.password != password:
            flash("خطأ: كلمة المرور غير مطابقة للمفتاح الخاص.", "danger")
            return False
            
        session['vendor_id'] = vendor.id
        session['brand_name'] = vendor.brand_name or "محجوب أونلاين"
        session['wallet'] = vendor.wallet_address # MAH Wallet
        return True
    except Exception as e:
        flash("عذراً، حدث خطأ في مزامنة البيانات.", "danger")
        return False

def logout_vendor():
    """إصلاح خطأ ImportError وتطهير الجلسة"""
    session.clear()
    flash("تم تسجيل الخروج من نظامك السيادي بنجاح.", "info")
    return redirect(url_for('login_page'))

def is_logged_in():
    return 'vendor_id' in session

def get_vendor_data():
    if is_logged_in():
        return Vendor.query.get(session['vendor_id'])
    return None
