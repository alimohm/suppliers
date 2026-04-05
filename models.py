from database import db
from datetime import datetime

class Vendor(db.Model):
    __tablename__ = 'vendor'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    brand_name = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=False)
    wallet = db.relationship('Wallet', backref='vendor', uselist=False, cascade="all, delete-orphan")
    staff = db.relationship('VendorStaff', backref='vendor', lazy=True, cascade="all, delete-orphan")

class VendorStaff(db.Model):
    __tablename__ = 'vendor_staff'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)

class Wallet(db.Model):
    __tablename__ = 'wallet'
    id = db.Column(db.Integer, primary_key=True)
    wallet_number = db.Column(db.String(50), unique=True)
    balance = db.Column(db.Float, default=0.0)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))

class AdminUser(db.Model):
    __tablename__ = 'admin_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

def seed_initial_data():
    admin = AdminUser.query.filter_by(username="علي محجوب").first()
    if not admin:
        new_admin = AdminUser(username="علي محجوب", password="123")
        db.session.add(new_admin)
        db.session.commit()
