from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20)) 
    brand_name = db.Column(db.String(100))
    wallet = db.relationship('Wallet', backref='owner', uselist=False, cascade="all, delete-orphan")
    products = db.relationship('Product', backref='supplier', lazy=True)

class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    wallet_number = db.Column(db.String(50), unique=True)
    balance = db.Column(db.Float, default=0.0)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(200))
    price = db.Column(db.Float)
    stock = db.Column(db.Integer, default=0)

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='علي محجوب').first():
            admin = User(username='علي محجوب', password='ali_password_2026', role='admin')
            db.session.add(admin)
            db.session.commit()
