from urllib.request import urlopen as o
import json as j
import requests
from gzip import GzipFile
from  io import BytesIO
from time import sleep

url = "http://cob.pythonanywhere.com/"
globalquery = "http://127.0.0.1:8080/query/torrents"
filesquery = "http://127.0.0.1:8080/query/propertiesFiles/{0}"
client = requests.session()
r = client.get(url)


def SetData(**kwarg):
    data = dict(kwarg)
    data["key"] = "65sdgdf56s4ghs56g4s6"
    return data

def Resp(path:str,data:dict):
    print(f"posting to : {path}")
    r = client.post(url + path,data=data)
    print(f"response : {r.text}")

setdata = True

while True:
    if setdata:
        data = o(globalquery).read()
        Resp("setdata/",SetData(data = data))
        

    loaded = j.loads(data)
    for line in loaded:
        if "hash" in line:
            hash = line['hash']
            torrent = o(filesquery.format(hash)).read().decode()
            if (torrent!=""):
                Resp("settorrentdata", SetData(torrent = torrent, hash = hash))
    sleep(1)