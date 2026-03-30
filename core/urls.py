from django.contrib import admin
from django.urls import path, include
from suppliers.views import dashboard
from django.shortcuts import redirect

# وظيفة لتحويل الزائر غير المسجل للدخول
def root_redirect(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    return redirect('/dashboard/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', include('django.contrib.auth.urls')), 
    path('dashboard/', dashboard, name='dashboard'),
    path('', root_redirect), # تحويل ذكي عند فتح الرابط الرئيسي
]
