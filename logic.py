from flask import session
from werkzeug.security import check_password_hash
from models import Vendor

def login_vendor(u, p):
    if not u or not p:
        return False, "يرجى إدخال اسم المستخدم وكلمة المرور."
        
    vendor = Vendor.query.filter_by(username=u).first()
    if not vendor:
        return False, "عذراً، هذا الحساب غير مسجل في المنصة اللامركزية."
    
    # التحقق الحقيقي من كلمة المرور (هذا ما سيمنع الدخول بأي رقم)
    if check_password_hash(vendor.password, p):
        session.clear()
        session['user_id'] = vendor.id
        session['role'] = 'vendor'
        return True, "تم الاتصال بنجاح."
    
    return False, "كلمة المرور غير صحيحة."
