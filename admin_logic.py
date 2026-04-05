from database import db
from models import AdminUser, Vendor, Wallet, Product, Transaction

def verify_admin_credentials(username, password):
    """التحقق من بيانات دخول المدير (علي محجوب) من قاعدة البيانات"""
    admin = AdminUser.query.filter_by(username=username).first()
    if admin and admin.password == password:
        return True, f"مرحباً بالقائد {username} في نظام الإدارة السيادي."
    return False, "بيانات الدخول غير صحيحة، يرجى المحاولة مرة أخرى."

def get_admin_stats():
    """جلب إحصائيات النظام الشاملة للعرض في لوحة التحكم"""
    try:
        total_vendors = Vendor.query.count()
        pending_vendors = Vendor.query.filter_by(is_active=False).count()
        total_products = Product.query.count()
        
        # حساب إجمالي السيولة في كافة المحافظ المرتبطة بنظام MAH
        total_liquidity = db.session.query(db.func.sum(Wallet.balance)).scalar() or 0.0
        
        return {
            'total_vendors': total_vendors,
            'pending': pending_vendors,
            'total_products': total_products,
            'total_liquidity': total_liquidity
        }
    except Exception as e:
        print(f"⚠️ تنبيه: تعذر جلب الإحصائيات كاملة (قد تكون الجداول فارغة): {e}")
        return {'total_vendors': 0, 'pending': 0, 'total_products': 0, 'total_liquidity': 0.0}

def get_dashboard_data():
    """جلب كافة الموردين المسجلين في Postgres"""
    return Vendor.query.all()

def approve_vendor_logic(vendor_id):
    """منطق تفعيل المورد، إنشاء محفظته، ومنحه الهوية المالية MAH"""
    vendor = Vendor.query.get(vendor_id)
    if not vendor:
        return False, "المورد غير موجود في النظام."
    
    if vendor.is_active:
        return False, "هذا المورد نشط بالفعل."

    try:
        # 1. تفعيل حساب المورد
        vendor.is_active = True
        
        # 2. توليد رقم محفظة فريد ونظامي للمورد
        if not vendor.wallet:
            import random
            wallet_no = f"MAH-{vendor_id}-{random.randint(1000, 9999)}"
            new_wallet = Wallet(wallet_number=wallet_no, balance=0.0, vendor_id=vendor.id)
            db.session.add(new_wallet)
        
        db.session.commit()
        return True, f"تم اعتماد المورد {vendor.brand_name} بنجاح وتفعيل محفظته الرقمية."
    except Exception as e:
        db.session.rollback()
        return False, f"فشل إجراء الاعتماد بسبب خطأ تقني: {str(e)}"
