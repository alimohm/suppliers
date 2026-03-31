
from flask import session
from database import Vendor

def perform_login(username, password):
    # المنطق: ابحث عن المورد الذي يطابق البيانات
    vendor = Vendor.query.filter_by(username=username, password=password).first()
    if vendor:
        session['vendor_id'] = vendor.id
        return True
    return False

def get_current_vendor():
    v_id = session.get('vendor_id')
    if v_id:
        return Vendor.query.get(v_id)
    return None
