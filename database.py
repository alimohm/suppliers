from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# الكلاس الذي تسبب في الخطأ (تم تصحيحه)
class SuperAdmin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20)) # admin or vendor
    brand_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    wallet = db.relationship('Wallet', backref='owner', uselist=False, cascade="all, delete-orphan")
    products = db.relationship('Product', backref='supplier', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, default=0.0)
    stock = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    wallet_number = db.Column(db.String(50), unique=True, nullable=False)
    balance = db.Column(db.Float, default=0.0)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'))
    tx_type = db.Column(db.String(50))
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
        # التأكد من وجود حساب علي محجوب كمدير للنظام
        if not User.query.filter_by(username='علي محجوب').first():
            admin = User(username='علي محجوب', password='ali_password_2026', role='admin')
            db.session.add(admin)
            db.session.commit()
