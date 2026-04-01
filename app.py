import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db
from logic import login_vendor, logout, is_logged_in
from sync_service import send_to_qumra_webhook # استيراد من الملف المستقل

app = Flask(__name__)
app.config.from_object(Config)

# ربط قاعدة البيانات
init_db(app)

@app.route('/')
def index():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        user = request.form.get('username')
        pw = request.form.get('password')
        if login_vendor(user, pw):
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not is_logged_in():
        return redirect(url_for('login_page'))
    return render_template('dashboard.html')

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    if request.method == 'POST':
        p_name = request.form.get('name')
        p_price = request.form.get('price')
        p_desc = request.form.get('description')
        
        # استدعاء محرك المزامنة المستقل
        status = send_to_qumra_webhook(p_name, p_price, p_desc)
        
        if status:
            flash(f"✅ تم الرفع والمزامنة السيادية لـ {p_name}", "success")
        else:
            flash(f"⚠️ فشلت المزامنة الخارجية، تحقق من الإعدادات.", "warning")
            
        return redirect(url_for('dashboard'))

    return render_template('add_product.html')

@app.route('/logout')
def logout_route():
    return logout()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
