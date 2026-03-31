import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mahjoub_sovereign_2026')
    
    # بيانات الويب هوك من صورك السابقة
    WEBHOOK_URL = "https://mahjoub.online/api/webhooks/products"
    WEBHOOK_SECRET = "qmr_dcbbd1f6-d0a7-43ed-9b4c-4a9394be06b9"
    
    # القواعد المالية السيادية
    USD_TO_SAR = 3.8
    PROFIT_MARGIN = 1.30  # إضافة 30% ربح تلقائياً
