from django.http import HttpRequest, Http404,HttpResponse
from importlib import reload
from queue import Queue
import qbredir.dumper

data = open("qbredir/qbredir/data.json",mode="r").read()
torrents = {}

def CheckGet(request):
    if request.method == "GET":
        raise Http404("")

def home(request):
    assert isinstance(request, HttpRequest)
    reload(qbredir.dumper)
    content = qbredir.dumper.dump(data)
    return HttpResponse(content)

def setdata(request):
    global data

    CheckGet(request)
    response = "err"
    if CheckKey(request):
        if "data" in request.POST:
            data = request.POST["data"]
            response = "ok"

    return HttpResponse(response)

def getdata(request):
    CheckGet(request)
    response = ""
    global data

    if CheckKey(request):
        response = data

    return HttpResponse(response)

def settorrentdata(request):
    CheckGet(request)
    response = "err"
    global torrents
    if CheckKey(request):
        if "torrent" in request.POST and "hash" in request.POST:
            torrents[request.POST["hash"]] = request.POST["torrent"]
            response = "ok"
    return HttpResponse(response)

def files(request):
    content = ""
    if "hash" in request.GET:
        hash = request.GET["hash"]
        content += hash
        if hash in torrents:
            reload(qbredir.dumper)
            content = qbredir.dumper.dumpfiles(torrents[hash])
    else:
        content = "no hash found"

    return HttpResponse(content)

def getqueue(request):
    #CheckGet(request)
    global requested
    #if CheckKey(requested) and not requested.empty():
    if not requested.empty():
        return HttpResponse(requested.get())
    return HttpResponse("")

def CheckKey(request):
    return "key" in request.POST and request.POST["key"] == "65sdgdf56s4ghs56g4s6"


