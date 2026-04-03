from flask import session, flash, redirect, url_for
from models import Vendor

def login_vendor(username, password):
    """
    منطق تسجيل دخول الموردين للمنصة اللامركزية.
    """
    # 1. محاولة جلب المورد من قاعدة البيانات المطابقة للاسم المدخل
    vendor = Vendor.query.filter_by(username=username).first()
    
    # 2. التحقق من وجود المستخدم أولاً
    if not vendor:
        flash("عذراً، اسم المستخدم هذا غير مسجل في المنصة اللامركزية.", "danger")
        return False
    
    # 3. التحقق من مطابقة كلمة المرور للمستخدم الموجود في القاعدة
    if vendor.password != password:
        flash("كلمة المرور غير صحيحة، يرجى التأكد والمحاولة مرة أخرى.", "danger")
        return False

    # 4. في حال التطابق التام، يتم تفعيل الجلسة وتخزين البيانات اللامركزية
    session['username'] = vendor.username
    session['brand_name'] = vendor.brand_name
    session['wallet'] = vendor.wallet_address
    
    flash(f"تم تسجيل الدخول بنجاح. مرحباً بك {vendor.brand_name}", "success")
    return True

def is_logged_in():
    """التحقق مما إذا كان المورد مسجل دخوله حالياً"""
    return 'username' in session

def logout():
    """تطهير الجلسة وتأمين النظام عند الخروج"""
    session.clear()
    flash("تم تسجيل الخروج وتأمين الجلسة بنجاح.", "info")
    return redirect(url_for('login_page'))
