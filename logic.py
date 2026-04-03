from models import Vendor
from werkzeug.security import check_password_hash
from flask import session

def login_vendor(username, password):
    # البحث في جدول الموردين فقط
    vendor = Vendor.query.filter_by(username=username).first()
    if vendor and check_password_hash(vendor.password, password):
        session['user_id'] = vendor.id
        session['role'] = 'vendor'
        session['username'] = vendor.username
        return True, f"مرحباً بك في سوقك، {vendor.brand_name}"
    return False, "بيانات الدخول للمورد غير صحيحة"

def is_logged_in():
    return session.get('role') == 'vendor'
