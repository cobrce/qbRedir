from urllib.request import urlopen as o
import json as j
import requests
from gzip import GzipFile
from  io import StringIO 

url = "http://cob.pythonanywhere.com/"
local = "http://127.0.0.1:8080/query/torrents"
localfiles = "http://127.0.0.1:8080/query/propertiesFiles/{0}"
client = requests.session()
r = client.get(url)


def SetData(**kwarg):
    data = dict(kwarg)
    data["key"] = "65sdgdf56s4ghs56g4s6"
    return data

def Resp(path:str,data:dict):
    out= StringIO()
    with GzipFile(fileobj=out,mode="w") as gzip:
        gzip.write(j.dumps(data))
    r = client.post(url + path,data=out.getvalue,header = {
        'Content-Type':'application/json',
        'Transfer-Encoding': 'gzip',
        })
    print(r.text)

setdata = True
if setdata:
    data = o(local).read()
    Resp("setdata/",SetData(data = data))


hash = o(url + "getqueue").read().decode()
if hash == "":
    if data in globals() or data in locals():
        hash = j.loads(data)[0]["hash"]
    else:
        exit

file = o(localfiles.format(hash)).read()
Resp("settorrentdata", SetData(torrent = file, hash = hash))



