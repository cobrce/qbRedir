from django.http import HttpRequest, Http404,HttpResponse

def home(request):
    content = "Wow, so empty"
    return HttpResponse(content)