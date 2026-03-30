from django.http import HttpResponse

def home(request):
    return HttpResponse("<h1>[ Mahjoub Online ] Smart Market</h1><p>المنصة اللامركزية الأولى لحوكمة سلاسل التوريد الرقمية تعمل بنجاح!</p>")
