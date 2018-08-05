from django.http import HttpResponse

def home(request):
    return HttpResponse('<font face="verdana">Wow, such empty</font>')
