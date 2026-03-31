from database import Vendor

def perform_login(username, password):
    # مطابقة بيانات تسجيل الدخول
    vendor = Vendor.query.filter_by(username=username, password=password).first()
    if vendor:
        return vendor, "نجاح"
    return None, "خطأ في البيانات"

def get_current_vendor(vendor_id):
    if vendor_id:
        # استرجاع كائن المورد كاملاً من Postgres
        return Vendor.query.get(int(vendor_id))
    return None
