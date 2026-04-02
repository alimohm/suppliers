import random
import string
from database import db

def generate_mah_wallet():
    """توليد عنوان محفظة فريد يبدأ بـ MAH متبوع بـ 10 رموز"""
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return f"MAH-{suffix}"

class Vendor(db.Model):
    """جدول الموردين - يمثل الكيان اللامركزي للتاجر"""
    __tablename__ = 'vendor'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    
    # اسم العلامة التجارية (البراند الشخصي للتاجر)
    brand_name = db.Column(db.String(120), nullable=False)
    
    # المحفظة الرقمية الخاصة بـ "محجوب أونلاين"
    wallet_address = db.Column(db.String(255), unique=True, default=generate_mah_wallet)
    
    # توكن الربط مع متجر قمرة (اختياري)
    qomra_access_token = db.Column(db.Text, nullable=True)
    
    # علاقة مع المنتجات (One to Many)
    products = db.relationship('Product', backref='vendor_owner', lazy=True)

    def __repr__(self):
        return f'<Vendor {self.brand_name} (@{self.username})>'

class Product(db.Model):
    """جدول المنتجات - قلب منصة محجوب أونلاين اللامركزية"""
    __tablename__ = 'product'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    
    # --- الإضافات الجوهرية للبنية الاحترافية ---
    brand = db.Column(db.String(120), nullable=True)  # العلامة التجارية للمنتج
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='YER') # (YER, SAR, USD) العملة
    stock = db

@app.route('/dashboard')
def dashboard():
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    user_session = session.get('username') # هنا 'مشتاق الفقيه'
    
    # جلب بيانات المورد لضمان ظهور البراند الجديد في الهيكل
    vendor_data = Vendor.query.filter_by(username=user_session).first()
    
    # تحديث الاسم التجاري في الجلسة الحالية لضمان الدقة
    # العلامة التجارية: عمار الفقيه للتجارة
    vendor_brand = "عمار الفقيه للتجارة" 
    
    products_list = Product.query.filter_by(vendor_username=user_session).all()
    
    return render_template('dashboard.html', 
                           vendor=vendor_data, 
                           brand_name=vendor_brand, # نمرر البراند الجديد هنا
                           products=products_list)
