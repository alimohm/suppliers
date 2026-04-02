from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import secrets # المكتبة الأفضل لتوليد أكواد عشوائية آمنة
import string

db = SQLAlchemy()

# 1. جدول المستخدمين مع توليد محفظة عشوائية فريدة
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='admin')
    
    # --- قسم المحفظة الرقمية الذكية ---
    wallet_address = db.Column(db.String(100), unique=True) # العنوان العشوائي
    wallet_balance = db.Column(db.Float, default=0.0)      # الرصيد
    
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    
    # علاقات الربط
    products = db.relationship('Product', backref='author', lazy=True)
    orders = db.relationship('Order', backref='buyer', lazy=True)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        # توليد رقم محفظة عشوائي فريد عند التسجيل
        if not self.wallet_address:
            self.wallet_address = self.generate_wallet_id()

    def generate_wallet_id(self):
        """توليد كود عشوائي يبدأ بـ MAH متبوع بـ 10 رموز معقدة"""
        chars = string.ascii_uppercase + string.digits
        # توليد 10 رموز عشوائية (أرقام وحروف كبيرة)
        random_code = ''.join(secrets.choice(chars) for _ in range(10))
        return f"MAH-{random_code}"

# 2. جدول المجموعات (Categories)
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    products = db.relationship('Product', backref='category', lazy=True)

# 3. جدول الموردين (بيانات إدارية)
class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20))
    products = db.relationship('Product', backref='supplier', lazy=True)

# 4. جدول المنتجات
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), nullable=False) # (USD, YER, SAR)
    stock = db.Column(db.Integer, default=0)
    media_data = db.Column(db.Text) # مسارات الصور والفيديو
    
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id')) # صاحب المنتج
    
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

# 5. جدول الطلبات (Orders)
class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    date_ordered = db.Column(db.DateTime, default=datetime.utcnow)

# 6. سجل المحفظة (Wallet Transactions)
class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    wallet_address = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20)) # (إيداع، سحب، شراء)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
