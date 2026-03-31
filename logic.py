from database import Vendor

def perform_login(username, password):
    """
    التحقق الصارم من قاعدة البيانات لمنع الدخول العشوائي
    """
    # البحث عن المورد الذي يطابق كل من اسم المستخدم وكلمة المرور معاً
    vendor = Vendor.query.filter_by(username=username, password=password).first()
    
    if vendor:
        # نجاح المطابقة مع قاعدة البيانات
        return vendor, "تم تسجيل الدخول بنجاح إلى النظام اللامركزي."
    
    # في حال عدم التطابق، نتحقق من السبب لإظهار الرسالة الصحيحة
    existing_user = Vendor.query.filter_by(username=username).first()
    if not existing_user:
        return None, "هذا المستخدم غير مسجل في المنصة اللامركزية."
    else:
        return None, "كلمة المرور غير صحيحة، يرجى إعادة المحاولة."

def get_current_vendor(vendor_id):
    if vendor_id:
        return Vendor.query.get(vendor_id)
    return None
