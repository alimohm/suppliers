import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db, Vendor

# استيراد الملفات المنفصلة (حتى لو تعطل أحدها، يسهل حصره)
try:
    import logic
    import finance
except ImportError:
    # نظام حماية في حال فقدان ملفات المنطق
    logic = None
    finance = None

# 1. تهيئة التطبيق والقاعدة
app = Flask(__name__)
app.config.from_object(Config)
init_db(app)

# 2. حجر الأساس: إنشاء الجداول والحساب الملكي
with app.app_context():
    try:
        db.create_all() 
        if not Vendor.query.filter_by(username="ali").first():
            db.session.add(Vendor(
                username="ali", 
                password="123", 
                owner_name="علي محجوب", 
                brand_name="محجوب أونلاين"
            ))
            db.session.commit()
    except Exception as e:
        print(f"فشل في تهيئة القاعدة: {e}")

# 3. بوابة الدخول (مستقلة تماماً عن باقي الوظائف)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'vendor_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = Vendor.query.filter_by(username=username).first()
        
        if user and user.password == password:
            session.permanent = True
            session['vendor_id'] = user.id
            return redirect(url_for('dashboard'))
        
        flash("خطأ في بيانات الدخول: يرجى التحقق من الاسم أو كلمة المرور", "error")
            
    return render_template('login.html')

# 4. لوحة الهيكل (تعتمد على logic.py إذا كان متاحاً)
@app.route('/dashboard')
def dashboard():
    if 'vendor_id' not in session:
        return redirect(url_for('login'))
        
    vendor = Vendor.query.get(session['vendor_id'])
    
    # محاولة جلب البيانات من logic.py دون تعطيل الصفحة
    stats = {}
    if logic:
        try: stats = logic.get_dashboard_stats(vendor.id)
        except: pass
        
    return render_template('dashboard.html', vendor=vendor, stats=stats)

# 5. التوجيه الذكي عند فتح الرابط الرئيسي
@app.route('/')
def home():
    return redirect(url_for('dashboard')) if 'vendor_id' in session else redirect(url_for('login'))

# 6. تسجيل الخروج
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    # تفعيل debug=True ليخبرك المتصفح بمكان الخطأ بالضبط إذا حدث
    app.run(host='0.0.0.0', port=port, debug=True)
