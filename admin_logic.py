import random
from database import db
from models import Vendor, Wallet, Transaction, AdminStaff, SuperAdmin

# 1. نظام التحقق من الهوية (برج المراقبة)
def verify_admin_credentials(username, password):
    """التحقق من دخول علي محجوب أو طاقم الإدارة المصرح له"""
    admin = SuperAdmin.query.filter_by(username=username, password=password).first()
    if admin:
        return True, "مرحباً بك يا سيد علي في لوحة التحكم المركزية."
    
    staff = AdminStaff.query.filter_by(username=username, password=password, is_active=True).first()
    if staff:
        return True, f"مرحباً {staff.username} (دخول طاقم الإدارة)."
    
    return False, "⚠️ بيانات الدخول غير صحيحة أو الحساب غير نشط."

# 2. إحصائيات المنصة اللامركزية (MAH Stats)
def get_admin_stats():
    """توليد تقرير حي عن حالة الموردين والسيولة المالية الكلية"""
    stats = {
        'total': Vendor.query.count(),
        'pending': Vendor.query.filter_by(status='قيد الانتظار').count(),
        'active': Vendor.query.filter_by(status='نشط').count(),
        'blocked': Vendor.query.filter_by(status='محظور').count(),
        # حساب إجمالي السيولة في كافة محافظ MAH الموجودة في النظام
        'liquidity': db.session.query(db.func.sum(Wallet.balance)).scalar() or 0.0
    }
    return stats

# 3. محرك جلب البيانات (الحل لخطأ الـ 500)
def get_dashboard_data():
    """جلب كافة الموردين لظهورهم في صفحة الاعتماد - مرتبين بالأحدث"""
    return Vendor.query.order_by(Vendor.created_at.desc()).all()

# 4. منطق التحكم السيادي (اعتماد / رفض / حظر)
def approve_vendor_logic(vendor_id, action):
    """
    إدارة حالة المورد المالية والقانونية.
    عند الاعتماد يتم تدشين المحفظة السيادية وتسجيل أول عملية في كشف الحساب.
    """
    vendor = Vendor.query.get(vendor_id)
    if not vendor:
        return False, "❌ خطأ: المورد غير موجود في قاعدة البيانات."

    if action == 'approve':
        vendor.status = 'نشط'
        vendor.is_active = True
        
        # إنشاء المحفظة MAH إذا لم تكن موجودة مسبقاً
        if not vendor.wallet:
            wallet_no = f"MAH-{random.randint(100000, 999999)}"
            new_wallet = Wallet(wallet_number=wallet_no, vendor_id=vendor.id, balance=0.0)
            db.session.add(new_wallet)
            db.session.flush() # الحصول على ID المحفظة قبل التسجيل
            
            # تسجيل عملية "تدشين" في كشف الحساب (Statement)
            log_system_tx(new_wallet.id, 0.0, "تم اعتماد الهوية وتفعيل المحفظة السيادية")
            
    elif action == 'reject':
        vendor.status = 'مرفوض'
        vendor.is_active = False
    
    elif action == 'block':
        vendor.status = 'محظور'
        vendor.is_active = False

    try:
        db.session.commit()
        return True, f"✅ تم تنفيذ الإجراء ({action}) على حساب المورد بنجاح."
    except Exception as e:
        db.session.rollback()
        return False, f"❌ فشل الحفظ في قاعدة البيانات: {str(e)}"

# 5. محرك كشف الحساب (System Ledger)
def log_system_tx(wallet_id, amount, details):
    """تسجيل العمليات التي يقوم بها النظام أو الإدارة في كشف حساب المورد"""
    wallet = Wallet.query.get(wallet_id)
    if wallet:
        new_tx = Transaction(
            wallet_id=wallet_id,
            tx_type='نظام',
            amount=amount,
            prev_balance=wallet.balance,
            new_balance=wallet.balance + amount,
            details=details
        )
        db.session.add(new_tx)
        return True
    return False
