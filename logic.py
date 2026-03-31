import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import db, init_db, Vendor
import logic

app = Flask(__name__)

# مفتاح سري لتأمين الجلسات والرسائل (Flash Messages)
app.secret_key = os.environ.get('SECRET_KEY', 'mahjoub_online_royal_2026')

# تهيئة قاعدة البيانات (الاتصال بـ Postgres في ريلوي)
init_db(app)

@app.route('/')
def index():
    # توجيه تلقائي لصفحة الدخول بمجرد فتح الرابط
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    # إذا كان المستخدم مسجل دخول بالفعل، يذهب للوحة التحكم مباشرة
    if 'vendor_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # استدعاء المنطق من ملف logic.py للتحقق من قاعدة البيانات
        vendor_obj, message = logic.perform_login(username, password)
        
        if vendor_obj:
            # نجاح الدخول: حفظ المعرف في الجلسة
            session['vendor_id'] = vendor_obj.id
            return redirect(url_for('dashboard'))
        else:
            # فشل الدخول: إظهار الرسالة العربية المتناسقة (غير مسجل أو كلمة مرور خاطئة)
            flash(message)
            
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # التحقق من أن المورد مسجل دخول
    vendor_id = session.get('vendor_id')
    vendor = logic.get_current_vendor(vendor_id)
    
    if not vendor:
        # إذا حاول الدخول للرابط مباشرة دون تسجيل، نعيده للبوابة
        return redirect(url_for('login'))
        
    return render_template('dashboard.html', vendor=vendor)

@app.route('/logout')
def logout():
    # إنهاء الجلسة والعودة لصفحة الدخول
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    # التشغيل على المنفذ 8080 المعتمد في ريلوي
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
