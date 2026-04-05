from models import Vendor, VendorStaff, Wallet
from database import db

def login_vendor(username, password):
    """
    التحقق من بيانات المورد أو موظفه
    الربط: يبحث في جدول Vendor وجدول VendorStaff
    """
    # 1. البحث في جدول أصحاب المتاجر (Owners)
    vendor = Vendor.query.filter_by(username=username, password=password).first()
    if vendor:
        if vendor.status == 'محظور':
            return False, None, "الحساب محظور حالياً"
        return True, vendor, 'vendor_owner'

    # 2. البحث في جدول موظفي الموردين (Staff)
    staff = VendorStaff.query.filter_by(username=username, password=password).first()
    if staff:
        # جلب بيانات المورد الأصلي المرتبط به الموظف
        owner = Vendor.query.get(staff.vendor_id)
        return True, owner, 'vendor_staff'

    return False, None, "بيانات الدخول غير صحيحة"
