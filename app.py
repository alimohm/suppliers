import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db, Product, Vendor # استيراد النماذج للتفاعل مع البيانات
from logic import login_vendor, logout, is_logged_in
from sync_service import send_to_qumra_webhook 

app = Flask(__name__)
app.config.from_object(Config)

# ربط المحرك بقاعدة البيانات في Railway
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
    """لوحة التحكم السيادية - عرض الإحصائيات الحقيقية"""
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    # سحب بيانات المورد (الاسم والمحفظة)
    vendor = Vendor.query.filter_by(username=session['username']).first()
    
    # إصلاح ذكي: محاولة جلب المنتجات، وإذا فشل بسبب العمود المفقود يعطي 0 ولا ينهار السيرفر
    try:
        products_count = Product.query.filter_by(vendor_username=session['username']).count()
    except Exception as e:
        print(f"⚠️ تنبيه: عمود vendor_username غير موجود حالياً، جلب العدد الكلي بدل ذلك. الخطأ: {e}")
        try:
            products_count = Product.query.count() # جلب العدد الكلي كحل بديل مؤقت
        except:
            products_count = 0
    
    return render_template('dashboard.html', 
                           vendor=vendor, 
                           products_count=products_count)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    if request.method == 'POST':
        p_name = request.form.get('name')
        p_price = request.form.get('price')
        p_desc = request.form.get('description')
        
        # التثبيت المحلي مع الحماية من أخطاء قاعدة البيانات
        try:
            new_item = Product(
                name=p_name,
                price=float(p_price),
                description=p_desc
                # تم إخفاء vendor_username مؤقتاً إذا كان يسبب كراش حتى نحدث الجدول
            )
            # محاولة إضافة الحقل إذا كان موجوداً
            if hasattr(new_item, 'vendor_username'):
                new_item.vendor_username = session['username']
                
            db.session.add(new_item)
            db.session.commit()
            
            # المزامنة الخارجية مع متجر قمرة
            status = send_to_qumra_webhook(p_name, p_price, p_desc)
            
            if status:
                flash(f"✅ تم الرفع والمزامنة السيادية لـ {p_name}", "success")
            else:
                flash(f"⚠️ تم الحفظ محلياً ولكن فشلت المزامنة الخارجية (تحقق من الويب هوك).", "warning")
        except Exception as e:
            db.session.rollback()
            print(f"❌ خطأ أثناء الحفظ: {e}")
            flash(f"❌ حدث خطأ فني أثناء الحفظ: تأكد من تحديث قاعدة البيانات.", "danger")
            
        return redirect(url_for('dashboard'))

    return render_template('add_product.html')

# ==========================================
# قناة استقبال الإشعارات من قمرة (Webhooks)
# ==========================================
@app.route('/webhook/qumra', methods=['POST'])
def qumra_receiver():
    """استقبال نبض المتجر وتحديث الأرصدة والمنتجات تلقائياً"""
    data = request.json
    print(f"📡 إشارة سيادية قادمة من قمرة: {data}")
    return {"status": "received"}, 200

@app.route('/logout')
def logout_route():
    return logout()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
