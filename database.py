import os
import random
import string
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    wallet_address = db.Column(db.String(255), unique=True)
    brand_name = db.Column(db.String(120))

def generate_mah_wallet():
    """توليد محفظة تبدأ بـ MAH متبوعة بـ 10 رموز عشوائية"""
    # توليد 10 رموز عشوائية كبيرة وأرقام
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
            db.create_all()
            # التأكد من وجود حسابك بالبادئة الجديدة
            if not Vendor.query.filter_by(username='ali').first():
                admin_user = Vendor(
                    username='ali',
                    password='123',
                    brand_name='محجوب أونلاين',
                    wallet_address=generate_mah_wallet() # سيولد محفظة تبدأ بـ MAH
                )
                db.session.add(admin_user)
                db.session.commit()
        except Exception as e:
            print(f"Error: {e}")
            
# أضف هذا النموذج داخل ملف database.py
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(500)) # لتخزين رابط الصورة
    description = db.Column(db.Text)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id')) # ربط المنتج بمورد معين
