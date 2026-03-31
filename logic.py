from database import Vendor

def perform_login(username, password):
    vendor = Vendor.query.filter_by(username=username).first()
    if not vendor:
        return None, "عذراً، هذا المستخدم غير مسجل في المنصة اللامركزية."
    if vendor.password != password:
        return None, "كلمة المرور التي أدخلتها غير صحيحة."
    return vendor, "نجاح"
