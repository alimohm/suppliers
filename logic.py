from database import Vendor

def perform_login(username, password):
    # 1. البحث عن اسم المستخدم في القاعدة
    vendor = Vendor.query.filter_by(username=username).first()
    
    if not vendor:
        return None, "عذراً، هذا المستخدم غير مسجل في المنصة اللامركزية."
    
    # 2. مطابقة كلمة المرور بعد التأكد من وجود المستخدم
    if vendor.password != password:
        return None, "كلمة المرور التي أدخلتها غير صحيحة."
    
    # 3. نجاح العملية
    return vendor, "تم تسجيل الدخول بنجاح."
