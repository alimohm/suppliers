def approve_vendor_logic(vendor_id):
    vendor = Vendor.query.get(vendor_id)
    if not vendor or vendor.is_active:
        return False, "الطلب غير موجود أو مفعل مسبقاً."

    # 1. التفعيل
    vendor.is_active = True
    vendor.status = "نشط"
    
    # 2. إنشاء المحفظة
    new_wallet = Wallet(vendor_id=vendor.id)
    db.session.add(new_wallet)
    db.session.flush() # للحصول على id المحفظة قبل الحفظ النهائي
    
    # 3. تسجيل أول حركة في كشف الحساب (الحركة الكاملة)
    first_tx = Transaction(
        wallet_id=new_wallet.id,
        trans_type="تأسيس",
        amount=0.0,
        balance_after=0.0,
        description="تفعيل الحساب السيادي في محجوب أونلاين"
    )
    db.session.add(first_tx)
    
    db.session.commit()
    return True, f"تم اعتماد المورد {vendor.brand_name} وفتح سجله المالي."
