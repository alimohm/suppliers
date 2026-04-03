import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

# --- 1. تعريف التطبيق فوراً (لحل خطأ NameError) ---
app = Flask(__name__) #

# --- 2. استدعاء الإعدادات والقاعدة من ملفاتك الجاهزة ---
from config import Config
from database import db, init_db
from models import Product, Vendor, AdminUser, seed_admin

app.config.from_object(Config) #

# --- 3. استدعاء المنطق من ملف logic.py حصراً ---
from logic import login_vendor, is_logged_in #

# إعدادات الرفع والميديا
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True) #

# --- 4. تهيئة القاعدة وحل مشكلة الأعمدة (status) ---
init_db(app) #

with app.app_context():
    # تحديث الجداول لضمان وجود أعمدة (status, wallet_address)
    db.create_all() #
    # حقن بيانات الهوية الرقمية
    seed_admin() #

# --- 5. بوابات العبور (المسارات) ---

@app.route('/')
def home():
    if is_logged_in(): return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

# بوابة دخول المورد
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if is_logged_in(): return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        # تنظيف المدخلات لضمان الدقة
        u = request.form.get('username', '').strip() #
        p = request.form.get('password', '').strip()
        
        # استدعاء دالتك السيادية من logic.py
        success, message = login_vendor(u, p) #
        
        if success:
            flash(message, "success")
            return redirect(url_for('dashboard'))
        else:
            flash(message, "danger")
            
    return render_template('login.html')

# لوحة تحكم المورد
@app.route('/dashboard')
def dashboard():
    if not is_logged_in(): return redirect(url_for('login_page'))
    vendor = Vendor.query.get(session.get('user_id'))
    products = Product.query.filter_by(vendor_id=vendor.id).all()
    return render_template('dashboard.html', vendor=vendor, products=products)

# بوابة الخروج الآمن
@app.route('/logout')
def logout():
    session.clear() # مسح الجلسة السيادية
    flash("تم تأمين البوابات بنجاح.", "info") #
    return redirect(url_for('login_page'))

# --- 6. التشغيل النهائي على Railway ---
if __name__ == '__main__':
    # التشغيل على المنفذ 8080 المعتمد
    app.run(host='0.0.0.0', port=8080, debug=True) #
