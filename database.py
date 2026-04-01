import os
import random
import string
from flask_sqlalchemy import SQLAlchemy

# تعريف الكائن البرمجي لقاعدة البيانات
db = SQLAlchemy()

class Vendor(db.Model):
    """جدول الموردين فقط - نظام الحوكمة الرقمية"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False) # المفتاح الخاص
    wallet_address = db.Column(db.String(255), unique=True) # محفظة MQ
    brand_name = db.Column(db.String(120))

def generate_mq_wallet():
    """توليد عنوان محفظة MQ فريد"""
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return f"MQ-{suffix}"

def init_db(app):
    """تهيئة الاتصال وبناء جدول الموردين في Railway"""
    
    uri = os.environ.get('DATABASE_URL')
    
    # تصحيح بروتوكول الاتصال
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = uri or 'sqlite:///local.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        try:
            # بناء جدول الـ Vendor فقط
            db.create_all()
            
            # التأكد من وجود حساب 'ali'
            if not Vendor.query.filter_by(username='ali').first():
                admin_user = Vendor(
                    username='ali',
                    password='123',
                    brand_name='محجوب أونلاين',
                    wallet_address=generate_mq_wallet()
                )
                db.session.add(admin_user)
                db.session.commit()
                print("✅ تم تحديث القاعدة وبناء جدول الموردين بنجاح.")
                
        except Exception as e:
            print(f"❌ خطأ: {e}")
