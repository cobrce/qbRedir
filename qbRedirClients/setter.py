from urllib.request import urlopen as o
import json as j
import requests
from gzip import GzipFile
from  io import BytesIO
from time import sleep
from threading import Thread

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
    #print(f"posting to : {path}")
    r = client.post(url + path,data=data)
    # print(f"response : {r.text}")

def ReadAndSendTorrent(hash):
    torrent = o(filesquery.format(hash)).read().decode()
    if (torrent!=""):
        Resp("settorrentdata", SetData(torrent = torrent, hash = hash))

def ParseTorrents(torrents):
    for torrent in torrents:
        if "hash" in torrent:
            hash = torrent['hash']
            t = Thread(target = lambda: ReadAndSendTorrent(hash))
            t.run()

def IsDownloading(torrent:dict):
    try:
        return torrent.get('state','unk') == 'downloading'
    except Exception as e:
        print (torrent)
    
setdata = True
i = 0

while True:
    # threads = list()
    i=(i+1)%4
    if setdata:
        data = o(globalquery).read()
        t = Thread(target = lambda : Resp("setdata/",SetData(data = data)))
        # t.run()
        # threads.append(t)
        
    loaded = j.loads(data)
    downloading = [torrent for torrent in loaded if IsDownloading(torrent)]

    for t in downloading:
        loaded.remove(t)

    ParseTorrents(downloading)
    if i == 3:
        ParseTorrents(loaded)
    sleep(1)