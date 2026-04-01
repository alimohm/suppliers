with app.app_context():
    # تحذير: هذا سيمسح المستخدمين الحاليين لإنشاء الهيكل الجديد
    # db.drop_all() 
    db.create_all()
