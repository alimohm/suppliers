from database import db
from models import Vendor, Wallet, Transaction, AdminStaff, SuperAdmin
import random

# 1. التحقق من بيانات الدخول
def verify_admin_credentials(username, password):
    admin = SuperAdmin.query.filter_by(username=username, password=password).first()
    if admin:
        return True, "مرحباً بك يا سيد علي."
    
    staff = AdminStaff.query.filter_by(username=username, password=password, is_active=True).first()
    if staff:
        return True, f"مرحباً {staff.full_name}."
    
    return False, "بيانات الدخول غير صحيحة."

# 2. جلب إحصائيات لوحة التحكم
def get_admin_stats():
    stats = {
        'total': Vendor.query.count(),
        'pending': Vendor.query.filter_by(status='قيد الانتظار').count(),
        'active': Vendor.query.filter_by(status='نشط').count(),
        'blocked': Vendor.query.filter_by(status='محظور').count(),
        'liquidity': db.session.query(db.func.sum(Wallet.balance)).scalar() or 0.0
    }
    return stats

# 3. الدالة التي تسببت في الخطأ (جلب بيانات الموردين لصفحة الاعتماد)
def get_dashboard_data():
    """هذه الدالة المطلوبة في app.py لجلب قائمة الموردين"""
    return Vendor.query.order_by(Vendor.created_at.desc()).all()

# 4. منطق قبول أو رفض المورد
def approve_vendor_logic(vendor_id, action):
    vendor = Vendor.query.get(vendor_id)
    if not vendor:
        return False, "المورد غير موجود."

    if action == 'approve':
        vendor.status = 'نشط'
        vendor.is_active = True
        # تأكد من إنشاء المحفظة إذا لم تكن موجودة
        if not vendor.wallet:
            wallet_no = f"MAH-{random.randint(100000, 999999)}"
            new_wallet = Wallet(wallet_number=wallet_no, vendor_id=vendor.id)
            db.session.add(new_wallet)
            db.session.flush()
            log_system_tx(new_wallet.id, 0.0, "افتتاح المحفظة عند الاعتماد")
            
    elif action == 'reject':
        vendor.status = 'مرفوض'
        vendor.is_active = False
    
    elif action == 'block':
        vendor.status = 'محظور'
        vendor.is_active = False

    db.session.commit()
    return True, f"تم تنفيذ الإجراء {action} بنجاح."

# 5. تسجيل العمليات النظامية
def log_system_tx(wallet_id, amount, details):
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
