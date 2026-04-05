from database import db
from datetime import datetime

# مودل الموردين
class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    brand_name = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=False)
    wallet = db.relationship('Wallet', backref='vendor', uselist=False)
    staff = db.relationship('VendorStaff', backref='vendor', lazy=True)

# 🛑 هذا الكلاس هو الذي كان ينقص ويسبب الانهيار 🛑
class VendorStaff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)

# مودل المحفظة
class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wallet_number = db.Column(db.String(20), unique=True)
    balance = db.Column(db.Float, default=0.0)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))

# مودل العمليات المالية
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20)) # شحن، سحب
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'))

# مودل المدير السيادي
class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

def seed_initial_data():
    """زرع بيانات المالك علي محجوب"""
    from database import db
    admin = AdminUser.query.filter_by(username="علي محجوب").first()
    if not admin:
        new_admin = AdminUser(username="علي محجوب", password="123")
        db.session.add(new_admin)
        db.session.commit()
        print("✅ تم إنشاء حساب علي محجوب بنجاح")
