import os
from flask import Flask, render_template, request, redirect, url_for, session
from database import db, init_db
import logic

app = Flask(__name__)
app.secret_key = 'mahjoub_king_2026'

# تهيئة قاعدة البيانات عند بدء التشغيل
init_db(app)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        if logic.perform_login(u, p):
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    vendor = logic.get_current_vendor()
    if not vendor:
        return redirect(url_for('login'))
    return render_template('dashboard.html', vendor=vendor)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
