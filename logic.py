from flask import session, flash, redirect, url_for
from models import Vendor

def login_vendor(username, password):
    """
    منطق تسجيل دخول الموردين المتوافق مع الهيكل اللامركزي الموحد.
    """
    try:
        # 1. جلب المورد من قاعدة البيانات
        vendor = Vendor.query.filter_by(username=username).first()
        
        # 2. التحقق من وجود المستخدم
        if not vendor:
            flash("عذراً، اسم المستخدم هذا غير مسجل في المنصة اللامركزية.", "danger")
            return False
        
        # 3. التحقق من مطابقة كلمة المرور (مع تحويلها لنص لمنع الانهيار)
        if str(vendor.password) != str(password):
            flash("كلمة المرور غير صحيحة، يرجى التأكد والمحاولة مرة أخرى.", "danger")
            return False

        # 4. تفعيل الجلسة مع إضافة الأوسمة التي يطلبها layout.html
        session['is_logged_in'] = True
        session['is_admin'] = False           # 💡 ضروري جداً لكي يعرف الهيكل أنك مورد وليس مديراً
        session['username'] = vendor.username  # ليظهر @username في الهيدر
        session['brand_name'] = vendor.brand_name
        session['wallet'] = vendor.wallet_address
        
        flash(f"🚀 تم تسجيل الدخول بنجاح. مرحباً بك في {vendor.brand_name}", "success")
        return True

    except Exception as e:
        print(f"DEBUG VENDOR LOGIN ERROR: {e}")
        flash("حدث خطأ تقني أثناء الدخول، يرجى المحاولة لاحقاً.", "danger")
        return False

def is_logged_in():
    """التحقق من حالة الدخول بناءً على وسم التفعيل"""
    return session.get('is_logged_in', False)

def logout():
    """تطهير الجلسة وتأمين النظام عند الخروج"""
    session.clear()
    flash("🔒 تم تسجيل الخروج وتأمين الجلسة بنجاح.", "info")
    return redirect(url_for('login_page'))
