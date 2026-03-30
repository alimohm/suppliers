from django.contrib import admin
from django.urls import path, include

# تخصيص نصوص لوحة التحكم لتناسب "سوقك الذكي"
admin.site.site_header = "Mahjoub Online - Smart Market"
admin.site.site_title = "لوحة تحكم الموردين"
admin.site.index_title = "إدارة سلاسل التوريد الرقمية"

urlpatterns = [
    # الرابط الذي ستفتحه هو /dashboard/
    path('dashboard/', admin.site.urls), 
    path('suppliers/', include('suppliers.urls')),
]
