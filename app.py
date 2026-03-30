import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'mahjoub_online_secure_2026'

# --- إعدادات قاعدة البيانات (Railway) ---
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- نماذج البيانات (Models) ---
class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    owner_name = db.Column(db.String(100))
    wallet_address = db.Column(db.String(100))

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))

# --- مسار الويب هوك (قمرة) ---
@app.route('/qamrah-webhook', methods=['POST'])
def qamrah_webhook():
    # التحقق من التوقيع السري الذي وضعته في لوحة قمرة
    signature = request.headers.get('X-Webhook-Signature')
    if signature != 'mahjoub_secret_2026':
        return jsonify({"error": "غير مصرح"}), 401
    
    data = request.json
    print(f"📦 استلام بيانات من قمرة: {data}")
    return jsonify({"status": "success"}), 200

# --- المسارات (Routes) ---
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        vendor = Vendor.query.filter_by(username=u, password=p).first()
        if vendor:
            session['vendor_id'] = vendor.id
            session['vendor_name'] = vendor.owner_name
            session['wallet'] = vendor.wallet_address
            return redirect(url_for('dashboard'))
        flash("بيانات الدخول غير صحيحة", "danger")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'vendor_id' not in session:
        return redirect(url_for('login'))
    products = Product.query.filter_by(vendor_id=session['vendor_id']).all()
    return render_template('dashboard.html', products=products)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- إنشاء الجداول وتجهيز الحساب الافتراضي ---
with app.app_context():
    db.create_all()
    if not Vendor.query.filter_by(username='ali').first():
        admin = Vendor(username='ali', password='123', owner_name='علي محجوب', wallet_address='MQ-5035D99C')
        db.session.add(admin)
        db.session.commit()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
