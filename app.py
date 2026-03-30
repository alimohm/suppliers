from flask import Flask, render_template, request, redirect, url_for, session
import os

# إخبار فلاسك بمكان المجلدات بدقة لضمان ظهور الواجهة
app = Flask(__name__, 
            template_folder='templates', 
            static_folder='static')

app.secret_key = "mahjoub_smart_key_2026"

@app.route('/')
def home():
    # توجيه تلقائي لصفحة الدخول ليكون الرابط نظيفاً
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # نظام دخول سريع للموردين
        user = request.form.get('username')
        if user: 
            session['user'] = user
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

if __name__ == '__main__':
    # التشغيل المتوافق مع Railway
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
