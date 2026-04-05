import os, random
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# موديول الجداول
class SuperAdmin(db.Model):
    id = db.Model.Column(db.Integer, primary_key=True)
    username = db.Model.Column(db.String(50), unique=True)
    password = db.Model.Column(db.String(255))

class Vendor(db.Model):
    id = db.Model.Column(db.Integer, primary_key=True)
    username = db.Model.Column(db.String(50), unique=True)
    password = db.Model.Column(db.String(255))
    brand_name = db.Model.Column(db.String(100))
    status = db.Model.Column(db.String(50), default='نشط')
    created_at = db.Model.Column(db.DateTime, default=datetime.utcnow)
    wallet = db.relationship('Wallet', backref='owner', uselist=False)
    products = db.relationship('Product', backref='supplier', lazy=True)

class Product(db.Model):
    id = db.Model.Column(db.Integer, primary_key=True)
    vendor_id = db.Model.Column(db.Integer, db.ForeignKey('vendor.id'))
    name = db.Model.Column(db.String(200))
    price = db.Model.Column(db.Float, default=0.0)
    stock = db.Model.Column(db.Integer, default=0)
    image_url = db.Model.Column(db.String(500))

class Wallet(db.Model):
    id = db.Model.Column(db.Integer, primary_key=True)
    vendor_id = db.Model.Column(db.Integer, db.ForeignKey('vendor.id'))
    wallet_number = db.Model.Column(db.String(50), unique=True)
    balance = db.Model.Column(db.Float, default=0.0)

class Transaction(db.Model):
    id = db.Model.Column(db.Integer, primary_key=True)
    wallet_id = db.Model.Column(db.Integer, db.ForeignKey('wallet.id'))
    tx_type = db.Model.Column(db.String(50))
    amount = db.Model.Column(db.Float)
    description = db.Model.Column(db.String(255))
    created_at = db.Model.Column(db.DateTime, default=datetime.utcnow)

def init_system(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
        if not SuperAdmin.query.filter_by(username='علي محجوب').first():
            db.session.add(SuperAdmin(username='علي محجوب', password='ali_password_2026'))
            db.session.commit()
