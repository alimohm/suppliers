from django.shortcuts import render

def home(request):
    # هنا يتم استدعاء بيانات سلاسل التوريد مستقبلاً
    return render(request, 'home.html')
