from database import db
from models import Vendor, Wallet, Transaction, AdminStaff, SuperAdmin
from datetime import datetime

def verify_admin_credentials(username, password):
    """التحقق من دخول علي محجوب أو طاقم الإدارة"""
    admin = SuperAdmin.query.filter_by(username=username, password=password).first()
    if admin: return True, "مرحباً بك يا علي."
    
    staff = AdminStaff.query.filter_by(username=username, password=password, is_active=True).first()
    if staff: return True, f"مرحباً {staff.full_name}."
    return False, "بيانات غير صحيحة."

def get_admin_stats():
    """إحصائيات المنصة الشاملة"""
    return {
        'total_vendors': Vendor.query.count(),
        'pending': Vendor.query.filter_by(status='قيد الانتظار').count(),
        'active': Vendor.query.filter_by(status='نشط').count(),
        'blocked': Vendor.query.filter_by(status='محظور').count(),
        'total_liquidity': db.session.query(db.func.sum(Wallet.balance)).scalar() or 0.0
    }

def approve_vendor_logic(vendor_id, action='approve'):
    """منطق القبول، الرفض، والحظر السيادي"""
    vendor = Vendor.query.get(vendor_id)
    if not vendor: return False, "المورد غير موجود"

    if action == 'approve':
        vendor.status = 'نشط'
        vendor.is_active = True
        # إنشاء المحفظة MAH إذا لم تكن موجودة
        if not vendor.wallet:
            import random
            wallet_no = f"MAH-{random.randint(100000, 999999)}"
            new_wallet = Wallet(wallet_number=wallet_no, vendor_id=vendor.id, balance=0.0)
            db.session.add(new_wallet)
            db.session.flush()
            # تدشين كشف الحساب
            log_system_tx(new_wallet.id, 0.0, "تدشين الحساب المالي والسيادة الرقمية")
        
    elif action == 'reject':
        vendor.status = 'مرفوض'
        vendor.is_active = False
    
    elif action == 'block':
        vendor.status = 'محظور'
        vendor.is_active = False

    db.session.commit()
    return True, f"تم تنفيذ الإجراء: {vendor.status}"

def log_system_tx(wallet_id, amount, details):
    """تسجيل العمليات الإدارية في كشف الحساب"""
    wallet = Wallet.query.get(wallet_id)
    new_tx = Transaction(
        wallet_id=wallet_id,
        tx_type='نظام',
        amount=amount,
        prev_balance=wallet.balance,
        new_balance=wallet.balance + amount,
        details=details
    )
    db.session.add(new_tx)
