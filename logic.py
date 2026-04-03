from flask import session
from werkzeug.security import check_password_hash
from models import Vendor

def login_vendor(username, password):
    vendor = Vendor.query.filter_by(username=username).first()
    if vendor and check_password_hash(vendor.password, password):
        if vendor.status != 'active':
            return False, "الحساب غير نشط."
        session.clear()
        session['user_id'] = vendor.id
        session['username'] = vendor.username
        session['role'] = 'vendor'
        return True, f"مرحباً بك: {vendor.brand_name}"
    return False, "بيانات الدخول خاطئة."

def is_logged_in():
    return 'user_id' in session and session.get('role') == 'vendor'
