import os
import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import db, init_db, Vendor
import logic

app = Flask(__name__)

# مفتاح التشفير للجلسات - يفضل وضعه في متغيرات بيئة ريلوي
app.secret_key = os.environ.get('SECRET_KEY', 'mahjoub_sovereign_2026_safe')

# إعدادات الربط التقني مع متجر محجوب أونلاين
MAHJOUB_API_KEY = "qmr_dcbbd1f6-d0a7-43ed-9b4c-4a9394be06b9"
STORE_URL = "https://mahjoub.online/api/v1/products" # رابط الأدوات (API)

# الثوابت المالية المنطقية
USD_TO_SAR = 3.8       # سعر التحويل الثابت
PROFIT_MARGIN = 1.30   # إضافة 30% كعمولة للمنصة

# تهيئة قاعدة البيانات Postgres في ريلوي
init_db(app)

@app.route('/')
def index():
    if 'vendor_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'vendor_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        
        # المنطق البرمجي للتحقق من الهوية (موجود في logic.py)
        vendor, message = logic.perform_login(u, p)
        
        if vendor:
            session['vendor_id'] = vendor.id
            return redirect(url_for('dashboard'))
        else:
            flash(message) # يظهر: (غير مسجل) أو (كلمة المرور خطأ)
            
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # حماية الهيكل من الدخول غير المصرح به
    vendor_id = session.get('vendor_id')
    if not vendor_id:
        return redirect(url_for('login'))
        
    # جلب بيانات المورد لعرضها في الهيكل (الاسم والمحفظة)
    vendor = Vendor.query.get(vendor_id)
    if not vendor:
        session.clear()
        return redirect(url_for('login'))
        
    return render_template('dashboard.html', vendor=vendor)

@app.route('/add_product', methods=['POST'])
def add_product():
    vendor_id = session.get('vendor_id')
    if not vendor_id:
        return redirect(url_for('login'))
    
    vendor = Vendor.query.get(vendor_id)
    
    # 1. استلام البيانات من نافذة الرفع
    name = request.form.get('name')
    try:
        cost_price = float(request.form.get('price'))
    except:
        flash("خطأ: يرجى إدخال سعر صحيح")
        return redirect(url_for('dashboard'))
        
    currency = request.form.get('currency') # SAR أو USD
    description = request.form.get('description')
    
    # 2. المنطق المالي: توحيد العملة للريال السعودي
    if currency == "USD":
        price_in_sar = cost_price * USD_TO_SAR
    else:
        price_in_sar = cost_price
        
    # 3. إضافة عمولة المتجر (30%) تلقائياً
    final_sale_price = round(price_in_sar * PROFIT_MARGIN, 2)
    
    # 4. تجهيز البيانات للنشر كمسودة (Draft) عبر الأدوات
    payload = {
        "api_key": MAHJOUB_API_KEY,
        "vendor_wallet": vendor.wallet_address,
        "product_name": name,
        "price": final_sale_price,
        "description": description,
        "status": "draft", # النشر كمسودة للمراجعة
        "vendor_note": f"Original Cost: {cost_price} {currency}"
    }
    
    try:
        # إرسال البيانات للمتجر (النشر الفعلي)
        response = requests.post(STORE_URL, json=payload, timeout=10)
        
        if response.status_code in [200, 201]:
            flash(f"تم رفع المنتج '{name}' كمسودة بنجاح. السعر النهائي للزبون: {final_sale_price} ر.س")
        else:
            flash("فشل الربط مع المتجر: تأكد من صحة الـ API Key")
            
    except Exception as e:
        flash("حدث خطأ تقني أثناء الاتصال بالمتجر")

    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    # فتح المنفذ المتوافق مع Railway
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
