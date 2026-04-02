import os
import random
import string
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()

# نموذج الموردين (Vendors)
class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    wallet_address = db.Column(db.String(255), unique=True)
    brand_name = db.Column(db.String(120))

# نموذج المنتجات (Products) - تم تحديثه ليدعم الصور المحلية
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(500)) # الرابط الخارجي (اختياري)
    image_file = db.Column(db.String(200)) # اسم ملف الصورة المرفوعة محلياً (ضروري للرفع الجديد)
    description = db.Column(db.Text)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
    vendor_username = db.Column(db.String(80)) 

def generate_mah_wallet():
    """توليد محفظة تبدأ بـ MAH متبوعة بـ 10 رموز عشوائية"""
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return f"MAH-{suffix}"

def init_db(app):
    uri = os.environ.get('DATABASE_URL')
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = uri or 'sqlite:///local.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        try:
            # 1. إنشاء الجداول الأساسية
            db.create_all()
            
            # 2. نظام "الترقيع الذكي" المطور لإضافة الأعمدة المفقودة تلقائياً
            columns_to_check = [
                ("vendor_username", "VARCHAR(80)"),
                ("image_file", "VARCHAR(200)") # العمود الجديد للصور المرفوعة
            ]
            
            for col_name, col_type in columns_to_check:
                try:
                    db.session.execute(text(f"SELECT {col_name} FROM product LIMIT 1"))
                except Exception:
                    db.session.rollback()
                    print(f"🚀 تحديث سيادي: جاري إضافة عمود {col_name} لجدول المنتجات...")
                    db.session.execute(text(f"ALTER TABLE product ADD COLUMN {col_name} {col_type}"))
                    db.session.commit()

            # 3. التأكد من وجود حسابك الإداري (علي)
            admin = Vendor.query.filter_by(username='ali').first()
            if not admin:
                admin_user = Vendor(
                    username='ali',
                    password='123',
                    brand_name='محجوب أونلاين',
                    wallet_address=generate_mah_wallet()
                )
                db.session.add(admin_user)
                db.session.commit()
                print("✅ تم إنشاء حساب الأدمن بنجاح.")
                
        except Exception as e:
            print(f"❌ خطأ في تهيئة قاعدة البيانات: {e}")
