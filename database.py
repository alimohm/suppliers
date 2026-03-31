import os, random, string
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def generate_wallet():
    return "MQ-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def init_db(app):
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url or 'sqlite:///local.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    owner_name = db.Column(db.String(100))
    wallet_address = db.Column(db.String(20), default=generate_wallet)
