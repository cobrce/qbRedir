from django.http import HttpRequest, Http404,HttpResponse

def home(request):
    content = '<font face="verdana">Wow, so empty</font>'
    return HttpResponse(content)