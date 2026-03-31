class Config:
    SECRET_KEY = "mahjoub_sovereign_2026"
    # رابط الويب هوك الذي تستخرجه من إعدادات قمرة (Webhooks)
    WEBHOOK_URL = "https://mahjoub.online/api/webhooks/products"
    # مفتاح التحقق (لضمان أن الطلب قادم من قمرة كلاود)
    WEBHOOK_SECRET = "qmr_dcbbd1f6-d0a7-43ed-9b4c-4a9394be06b9" 
    
    USD_TO_SAR = 3.8
    PROFIT_MARGIN = 1.30
