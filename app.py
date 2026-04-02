@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    if request.method == 'POST':
        # 1. استقبال البيانات من النافذة الاحترافية الجديدة
        p_name = request.form.get('p_name') 
        p_price = request.form.get('p_price')
        p_currency = request.form.get('p_currency', 'MAH') # استقبال العملة المحددة
        p_desc = request.form.get('p_desc', '') 
        
        # استقبال الوسائط (صور متعددة وفيديو)
        p_images = request.files.getlist('p_images') 
        p_video = request.files.get('p_video')

        if not p_name or not p_price:
            flash("❌ يرجى إدخال اسم المنتج وسعره.", "danger")
            return redirect(url_for('dashboard'))

        try:
            final_price = float(p_price)
            main_image_name = None

            # 2. ذكاء إعادة التسمية: تحويل الملفات لتأخذ اسم المنتج تلقائياً
            # سنقوم بتنظيف الاسم ليكون صالحاً كاسم ملف
            clean_name = secure_filename(p_name).replace(' ', '_')

            for index, img in enumerate(p_images):
                if img and img.filename != '':
                    ext = os.path.splitext(img.filename)[1]
                    # التسمية: اسم_المنتج_1.png
                    new_img_name = f"{clean_name}_{index+1}{ext}"
                    img.save(os.path.join(app.config['UPLOAD_FOLDER'], new_img_name))
                    
                    if index == 0:
                        main_image_name = new_img_name

            # 3. معالجة الفيديو (اختياري) وإعادة تسميته أيضاً
            if p_video and p_video.filename != '':
                v_ext = os.path.splitext(p_video.filename)[1]
                new_vid_name = f"{clean_name}_video{v_ext}"
                p_video.save(os.path.join(app.config['UPLOAD_FOLDER'], new_vid_name))

            # 4. الحفظ في قاعدة البيانات (دمج العملة في الوصف لضمان المزامنة)
            full_description = f"[{p_currency}] {p_desc}"
            
            new_item = Product(
                name=p_name,
                price=final_price,
                description=full_description,
                image_file=main_image_name, 
                vendor_username=session['username']
            )
            
            db.session.add(new_item)
            db.session.commit()
            
            # 5. المزامنة السيادية مع "قمرة" عبر GraphQL
            try:
                # نرسل السعر مع رمز العملة لضمان دقة البيانات الخارجية
                price_with_currency = f"{final_price} {p_currency}"
                status = send_to_qumra_webhook(p_name, price_with_currency, p_desc, main_image_name)
                
                if status:
                    flash(f"🚀 تم رفع {p_name} بنجاح. تم إعادة تسمية الصور لتطابق الهوية الرقمية!", "success")
                else:
                    flash(f"✅ تم الحفظ المحلي بنجاح، المزامنة الخارجية قيد المعالجة.", "info")
            except Exception as sync_err:
                print(f"📡 تنبيه مزامنة: {sync_err}")
                flash(f"⚠️ المنتج متاح في لوحتك، سيتم تحديث المتجر لاحقاً.", "warning")

            return redirect(url_for('dashboard'))

        except ValueError:
            flash("❌ خطأ: السعر يجب أن يكون رقماً.", "danger")
        except Exception as e:
            db.session.rollback()
            print(f"❌ خطأ فني: {e}")
            flash(f"❌ حدث خطأ غير متوقع أثناء المعالجة الملكية.", "danger")
            return redirect(url_for('dashboard'))

    # في حالة طلب الصفحة عبر GET، يتم توجيهه للداشبورد لأن النافذة منبثقة فيه
    return redirect(url_for('dashboard'))
