from database import db
from models import AdminUser, Vendor, Wallet

def verify_admin_credentials(username, password):
    admin = AdminUser.query.filter_by(username=username).first()
    if admin and admin.password == password:
        return True, f"مرحباً بالقائد {username}"
    return False, "خطأ في بيانات الدخول."

def get_admin_stats():
    total = Vendor.query.count()
    pending = Vendor.query.filter_by(is_active=False).count()
    return {'total_vendors': total, 'pending': pending}

def get_dashboard_data():
    return Vendor.query.all()

def approve_vendor_logic(vendor_id):
    vendor = Vendor.query.get(vendor_id)
    if vendor and not vendor.is_active:
        vendor.is_active = True
        if not vendor.wallet:
            import random
            wn = f"MAH-{random.randint(1000, 9999)}"
            db.session.add(Wallet(wallet_number=wn, vendor_id=vendor.id))
        db.session.commit()
        return True, "تم التفعيل."
    return False, "فشل التفعيل."
