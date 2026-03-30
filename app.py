import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'mahjoub_online_2026')

# --- ربط قاعدة البيانات ---
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- الجدول ---
class Vendor(db.Model):
    __tablename__ = 'vendors'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    owner_name = db.Column(db.String(100))
    brand_name = db.Column(db.String(100))

# --- إنشاء الجداول تلقائياً ---
def setup_db():
    if database_url:
        with app.app_context():
            try:
                db.create_all()
                if not Vendor.query.filter_by(username='ali').first():
                    admin = Vendor(username='ali', password='123', owner_name='علي محجوب', brand_name='محجوب أونلاين')
                    db.session.add(admin)
                    db.session.commit()
            except Exception as e:
                print(f"Database sync error: {e}")

setup_db()

# --- المسارات والمنطق المطلوب ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        vendor = Vendor.query.filter_by(username=u).first()
        
        if not vendor:
            flash("عذراً، هذا المورد غير مسجل في المنصة اللامركزية.", "danger")
        elif vendor.password != p:
            flash("كلمة المرور غير صحيحة، تأكد وحاول مجدداً.", "warning")
        else:
            session.update({'vendor_id': vendor.id, 'vendor_name': vendor.owner_name, 'brand_name': vendor.brand_name})
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'vendor_id' not in session: return redirect(url_for('login'))
    return f"لوحة تحكم {session['brand_name']} - المنصة اللامركزية"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
