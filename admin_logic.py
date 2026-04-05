from database import db
from datetime import datetime

class AdminUser(db.Model):
    id = db.Column(db.Column(db.Integer, primary_key=True))
    # أندكس لسرعة دخول الآدمن
    username = db.Column(db.String(80), unique=True, nullable=False, index=True) 
    password = db.Column(db.String(120), nullable=False)

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True) # مؤندكس تلقائياً لأنه Primary Key
    # أندكس لسرعة دخول الموردين
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    # أندكس لسرعة البحث عن البراند في برج المراقبة
    brand_name = db.Column(db.String(120), nullable=False, index=True)
    password = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    id_card_image = db.Column(db.String(255))
    commercial_registry_image = db.Column(db.String(255))
    # أندكس لسرعة الفلترة (نشط/معلق)
    status = db.Column(db.String(20), default="معلق", index=True)
    is_active = db.Column(db.Boolean, default=False, index=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # علاقة المحفظة
    wallet = db.relationship('Wallet', backref='vendor', uselist=False)

class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # أندكس لسرعة العمليات المالية والبحث برقم المحفظة
    wallet_number = db.Column(db.String(50), unique=True, index=True)
    balance = db.Column(db.Float, default=0.0)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), index=True)

    def __init__(self, **kwargs):
        super(Wallet, self).__init__(**kwargs)
        if not self.wallet_number:
            # توليد رقم المحفظة السيادي
            import random
            self.wallet_number = f"MAH-{random.randint(100000, 999999)}"
