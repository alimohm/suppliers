import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = "mahjoub_royal_key_2026"

# قاعدة بيانات تجريبية (سيتم ربطها بـ Postgres لاحقاً)
USERS = {
    "ali": "123456",
    "vendor01": "pass2026"
}

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()

        # منطق التحقق الذكي
        if username not in USERS:
            flash("عذراً، هذا المورد غير مسجل في المنصة اللامركزية.", "danger")
        elif USERS[username] != password:
            flash("كلمة المرور غير صحيحة، يرجى التأكد والمحاولة مجدداً.", "warning")
        else:
            session['user'] = username
            return redirect(url_for('dashboard'))
            
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    message = None
    if request.method == 'POST':
        p_name = request.form.get('p_name')
        try:
            p_price = float(request.form.get('p_price'))
            final_price = p_price * 1.40
            message = f"تم بنجاح حوكمة منتج ({p_name}) ورفعه بسعر {final_price:.2f} ريال."
        except:
            message = "خطأ في إدخال السعر، يرجى المحاولة مرة أخرى."

    return render_template('dashboard.html', message=message)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
