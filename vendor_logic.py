from database import db
from models import Vendor, VendorStaff, Wallet, Transaction, Product
from datetime import datetime

# --- [ 1. نظام الدخول الموحد (صاحب متجر + موظف) ] ---

def login_vendor(u, p):
    """
    محرك التحقق من الهوية: يفحص الحالات المنطقية (محظور، مقيد، مرفوض)
    ويمنح صلاحيات الدخول بناءً على نوع الحساب.
    """
    # 1. البحث أولاً في جدول الموردين (الملاك)
    vendor = Vendor.query.filter_by(username=u).first()
    
    if vendor:
        # أ: التحقق من الحالة السيادية (الحظر والتقييد)
        if vendor.status == "محظور":
            return False, "❌ عذراً، حسابك محظور نهائياً. يرجى التواصل مع الإدارة المركزية.", None
        
        if vendor.status == "مرفوض":
            return False, "🚫 تم رفض طلب انضمامك للمنصة. يمكنك تقديم طلب جديد لاحقاً.", None

        if not vendor.is_active:
            return False, "⚠️ حسابك غير نشط حالياً أو قيد المراجعة.", None
        
        # ب: التحقق من كلمة المرور
        if vendor.password == p:
            msg = f"مرحباً بك يا سيد {vendor.username} في مملكتك الرقمية (علي محجوب أونلاين)"
            return True, vendor, "vendor_owner"
        else:
            return False, "🔑 عذراً، كلمة المرور غير صحيحة. حاول مجدداً.", None

    # 2. إذا لم يكن مورداً، نبحث في جدول الموظفين
    staff = VendorStaff.query.filter_by(username=u).first()
    
    if staff:
        # التحقق من حالة المورد الأصلي (هل صاحب العمل محظور أو مقيد؟)
        parent_vendor = staff.employer # تم الربط عبر backref='employer' في models
        
        if parent_vendor.status == "محظور":
            return False, "❌ لا يمكن الدخول، حساب المورد التابع له الموظف محظور سيادياً.", None
            
        if not staff.is_active:
            return False, "⚠️ حساب الموظف الخاص بك موقوف حالياً.", None
            
        if staff.password == p:
            return True, parent_vendor, "vendor_staff"
        else:
            return False, "🔑 كلمة المرور للموظف غير صحيحة.", None

    # 3. إذا لم يجد الاسم في الجدولين نهائياً
    return False, "🚫 هذا الحساب غير مسجل في المنصة. تأكد من البيانات.", None


# --- [ 2. نظام كشف الحساب المالي (Statement) ] ---

def get_vendor_statement(vendor_id):
    """جلب كافة الحركات المالية المسجلة في محفظة MAH الخاصة بالمورد"""
    vendor = Vendor.query.get(vendor_id)
    if vendor and vendor.wallet:
        # جلب العمليات مرتبة من الأحدث للأقدم
        return Transaction.query.filter_by(wallet_id=vendor.wallet.id).order_by(Transaction.created_at.desc()).all()
    return []


# --- [ 3. إدارة المنتجات والعلامة التجارية ] ---

def get_my_products(vendor_id):
    """جلب المنتجات المرتبطة بالعلامة التجارية للمورد"""
    return Product.query.filter_by(vendor_id=vendor_id).all()

def add_new_product(vendor_id, data):
    """إضافة منتج جديد وتأمين ارتباطه بالمورد"""
    vendor = Vendor.query.get(vendor_id)
    
    # منع الإضافة إذا كان الحساب تحت الرقابة أو مقيد
    if vendor.status in ["مقيد", "تحت الرقابة"]:
        return False, "⚠️ حسابك مقيد حالياً، لا يمكنك إضافة منتجات جديدة."

    try:
        new_p = Product(
            vendor_id=vendor_id,
            name=data.get('name'),
            description=data.get('description'),
            price=float(data.get('price')),
            stock=int(data.get('stock')),
            image_url=data.get('image_url', 'default_product.png')
        )
        db.session.add(new_p)
        db.session.commit()
        return True, "✅ تم إضافة المنتج بنجاح لعلامتك التجارية."
    except Exception as e:
        db.session.rollback()
        return False, f"❌ خطأ في النظام: {str(e)}"


# --- [ 4. بيانات المحفظة MAH ] ---

def get_wallet_details(vendor_id):
    """جلب الرصيد ورقم المحفظة السيادي للمورد"""
    vendor = Vendor.query.get(vendor_id)
    if vendor and vendor.wallet:
        return {
            'wallet_number': vendor.wallet.wallet_number,
            'balance': vendor.wallet.balance,
            'currency': 'YER'
        }
    return None
