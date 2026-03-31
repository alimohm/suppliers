import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import db, init_db
import logic
# استدعاء الجسر الذي بنيناه (الحسابات، الصور، والربط بقمرة)
import bridge_logic 

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'mahjoub_king_2026')

# تهيئة قاعدة البيانات عند بدء التشغيل
init_db(app)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'vendor_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        
        vendor_obj, message = logic.perform_login(u, p)
        
        if vendor_obj:
            session['vendor_id'] = vendor_obj.id
            return redirect(url_for('dashboard'))
        else:
            flash(message)
            
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    vendor_id = session.get('vendor_id')
    vendor = logic.get_current_vendor(vendor_id)
    
    if not vendor:
        return redirect(url_for('login'))
        
    return render_template('dashboard.html', vendor=vendor)

# --- الجزء الجديد: استقبال ورفع منتجات الموردين ---
@app.route('/add_product', methods=['POST'])
def add_product():
    if 'vendor_id' not in session:
        return redirect(url_for('login'))

    # 1. استقبال البيانات من "واجهة المورد" التي صممناها
    p_name = request.form.get('name')
    p_desc = request.form.get('description')
    p_price = request.form.get('price')
    p_currency = request.form.get('currency') # تتوقع USD أو SAR
    p_image = request.files.get('image')      # استقبال أي صورة

    if p_name and p_price and p_image:
        # 2. تحويل السعر للريال وإضافة ربح 30% عبر الجسر
        final_sar_price = bridge_logic.calculate_final_price(p_price, p_currency)

        # 3. معالجة الصورة وتحويلها لـ WebP لضمان سرعة المتجر
        processed_img = bridge_logic.process_product_image(p_image)

        # 4. الإرسال لمتجر قمرة كمسودة (Draft) للمراجعة
        success = bridge_logic.push_to_qmr_store(p_name, p_desc, final_sar_price, processed_img)

        if success:
            flash("تم رفع المنتج بنجاح! سيظهر في المتجر بعد مراجعته.")
        else:
            flash("حدث خطأ تقني أثناء الربط بمتجر قمرة.")
    else:
        flash("يرجى إكمال جميع الحقول ورفع صورة المنتج.")

    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
