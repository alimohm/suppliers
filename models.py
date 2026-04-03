import random
import string
from datetime import datetime
from database import db

def generate_mah_wallet():
    """توليد عنوان محفظة فريد يبدأ بـ MAH متبوع بـ 10 رموز"""
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return f"MAH-{suffix}"

class Vendor(db.Model):
    """جدول الموردين والموظفين - الكيان اللامركزي لمحجوب أونلاين"""
    __tablename__ = 'vendor'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # بيانات الدخول للموظف (مثلاً: username: mushtaq)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    
    # الحقول التشغيلية
    employee_name = db.Column(db.String(120), nullable=True) 
    brand_name = db.Column(db.String(120), nullable=False)    
    
    # --- صلاحيات المدير العام ---
    is_active = db.Column(db.Boolean, default=True) # تجميد أو تفعيل المورد
    
    # الهوية الرقمية اللامركزية للمؤسسة
    wallet_address = db.Column(db.String(255), unique=True, default=generate_mah_wallet)
    
    # توكن الربط الخارجي (Qomra وغيره)
    qomra_access_token = db.Column(db.Text, nullable=True)
    
    # علاقة المنتجات
    products = db.relationship('Product', backref='vendor_owner', lazy=True)

    def __repr__(self):
        return f'<Vendor Employee: {self.employee_name} | Brand: {self.brand_name}>'

class Product(db.Model):
    """جدول المنتجات - قلب منصة محجوب أونلاين اللامركزية"""
    __tablename__ = 'product'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    brand = db.Column(db.String(120), nullable=True)  
    
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='YER') 
    stock = db.Column(db.Integer, default=1)           
    
    # المحتوى والوسائط
    description = db.Column(db.Text)
    image_file = db.Column(db.Text) # يخزن مسارات الصور والفيديو
    
    # --- حقول التحكم الإداري (صبري) ---
    status = db.Column(db.String(20), default='pending') # pending, approved, rejected
    is_published = db.Column(db.Boolean, default=False)
    
    # الربط التقني
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id')) 
    vendor_username = db.Column(db.String(80))                    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Product {self.name} - Status: {self.status}>'

class AdminUser(db.Model):
    """جدول الإدارة المركزية - برج المراقبة"""
    __tablename__ = 'admin_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# --- دالة مساعدة لحقن بياناتك (صبري) تلقائياً ---
def seed_admin():
    """تأكد من وجود حساب صبري في قاعدة البيانات"""
    admin = AdminUser.query.filter_by(username='صبري').first()
    if not admin:
        new_admin = AdminUser(username='صبري', password='123')
        db.session.add(new_admin)
        db.session.commit()
        print("✅ تم تفعيل حساب المدير العام: صبري")
