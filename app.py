import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import db, init_db, Vendor
import logic  # استدعاء ملف المنطق المنفصل

app = Flask(__name__)
# ضبط المسارات لضمان رؤية المجلدات الصحيحة
app.template_folder = os.path.abspath('templates')
app.secret_key = 'mahjoub_online_2026_key' # مفتاح الأمان للتشفير

# 1. تهيئة قاعدة البيانات عند التشغيل
init_db(app)

# 2. بوابة الدخول (المسار الوحيد للدالة login)
@app.route('/login', methods=['GET', 'POST'])
def login():
    # منع الدخول المتكرر إذا كانت الجلسة نشطة
    if 'vendor_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # استدعاء منطق التحقق من ملف logic.py
        # تأكد أن الدالة في logic.py اسمها do_login_check
        result = logic.do_login_check(username, password)
        
        if result['status']:
            session.permanent = True
            session['vendor_id'] = result['user'].id
            return redirect(url_for('dashboard'))
        else:
            # إظهار رسالة الخطأ باللون الأحمر في القسم البنفسجي
            flash(result['message'], "error")
            
    # عرض الواجهة المعكوسة (أبيض يمين، بنفسجي يسار)
    return render_template('login.html')

# 3. توجيه الرابط الرئيسي
@app.route('/')
def index():
    return redirect(url_for('login'))

# 4. لوحة التحكم (مؤقتة لاختبار النجاح)
@app.route('/dashboard')
def dashboard():
    if 'vendor_id' not in session:
        return redirect(url_for('login'))
    return "تم تسجيل الدخول بنجاح إلى لوحة محجوب أونلاين"

if __name__ == "__main__":
    # التشغيل على منفذ 8080 المتوافق
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
