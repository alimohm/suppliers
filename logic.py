# logic.py
from database import Vendor

def execute_authentication(username, password): 
    """دالة التحقق المستقلة تماماً"""
    user = Vendor.query.filter_by(username=username).first()
    if user and user.password == password:
        return {"status": True, "user": user}
    return {"status": False, "message": "بيانات الدخول غير صحيحة"}
