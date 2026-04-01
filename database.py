def init_db(app):
    uri = os.environ.get('DATABASE_URL')
    
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    
    app.config.update(
        SQLALCHEMY_DATABASE_URI=uri or 'sqlite:///local.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY=os.environ.get('SK', 'MAHJOUB_SECURE_2026')
    )
    
    db.init_app(app)
    
    with app.app_context():
        # الخطوة السيادية: مسح الجداول القديمة لإعادة بنائها بالهيكل الجديد
        # ملاحظة: سيتم حذف البيانات التجريبية الحالية لإصلاح الخطأ
        db.drop_all() 
        db.create_all()
        
        # إضافة مستخدمك 'ali' تلقائياً لضمان قدرتك على الدخول فوراً
        if not Vendor.query.filter_by(username='ali').first():
            new_v = Vendor(
                username='ali',
                password='123',
                owner_name='علي محجوب',
                brand_name='محجوب أونلاين',
                wallet_address='MQ-5035D99C'
            )
            db.session.add(new_v)
            db.session.commit()
