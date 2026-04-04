from models import Vendor, VendorStaff

def login_vendor(username, password):
    # البحث في جدول الملاك (علي محمد)
    vendor = Vendor.query.filter_by(username=username, password=password).first()
    if vendor:
        return True, "مرحباً بك يا سيد " + vendor.username, "vendor_owner"

    # البحث في جدول الموظفين (الموظف التجريبي)
    staff = VendorStaff.query.filter_by(username=username, password=password).first()
    if staff:
        return True, "دخول ناجح للموظف: " + staff.username, "vendor_staff"

    return False, "بيانات الدخول غير صحيحة", None
