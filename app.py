import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# مفتاح أمان قوي لضمان استقرار الجلسة (Session)
app.secret_key = os.environ.get('SECRET_KEY', 'mahjoub_online_2026_key')

# --- إعداد الاتصال بقاعدة بيانات Railway ---
db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- تعريف الجداول الموحدة (المفردة) ---
class Vendor(db.Model):
    __tablename__ = 'vendor'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    owner_name = db.Column(db.String(100))
    wallet_address = db.Column(db.String(100))

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))

# --- المسارات (Routes) ---

@app.route('/dashboard')
def dashboard():
    if 'vendor_id' not in session:
        return redirect(url_for('login'))
    
    # جلب بيانات المورد بأمان لتجنب خطأ 500
    vendor_data = Vendor.query.get(session['vendor_id'])
    
    if not vendor_data:
        session.clear()
        return redirect(url_for('login'))
    
    # جلب منتجات هذا المورد فقط من الجدول الصحيح
    products_list = Product.query.filter_by(vendor_id=vendor_data.id).all()
    
    return render_template('dashboard.html', 
                           vendor=vendor_data, 
                           products=products_list)

@app.route('/upload_product', methods=['POST'])
def upload_product():
    if 'vendor_id' not in session:
        return redirect(url_for('login'))
    
    # استقبال البيانات من الفورم الموجود في dashboard.html
    name = request.form.get('name')
    price = request.form.get('price')
    description = request.form.get('description')
    
    if name and price:
        try:
            # إنشاء منتج جديد وربطه بمعرف المورد الحالي
            new_product = Product(
                name=name, 
                price=float(price), 
                description=description, 
                vendor_id=session['vendor_id']
            )
            db.session.add(new_product)
            db.session.commit()
            flash("تم رفع المنتج بنجاح والمزامنة مع نظام قمرة")
        except Exception as e:
            db.session.rollback()
            print(f"Error saving product: {e}")
            flash("حدث خطأ أثناء الحفظ في القاعدة")
            
    return redirect(url_for('dashboard'))

# إضافة مسار تسجيل الخروج لتنظيف الجلسة
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    # تشغيل السيرفر على المنفذ الذي يحدده Railway
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
