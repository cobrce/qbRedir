from urllib.request import urlopen as o
import json as j
import requests

url = "http://cob.pythonanywhere.com/"
local = "http://127.0.0.1:8080/query/torrents"
localfiles = "http://127.0.0.1:8080/query/propertiesFiles/{0}"
client = requests.session()
r = client.get(url)


def SetData(**kwarg):
    data = dict(kwarg)
    data["key"] = "65sdgdf56s4ghs56g4s6"
    data["username"] = "cob"
    data["password"] = "5311241"
    return data

def Resp(path:str,data:dict):
    r = client.post(url + path,data=data)
    print(r.text)

setdata = False
if setdata:
    data = o(local).read()
    Resp("setdata/",SetData(data = data))


hash = o(url + "getqueue").read().decode()
if hash == "":
    hash = j.loads(data)[0]["hash"]

file = o(localfiles.format(hash)).read()
Resp("settorrentdata", SetData(torrent = file, hash = hash))



