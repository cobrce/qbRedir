import sys
from subprocess import Popen
from urllib.request import urlopen as o
import json as j
import requests
from gzip import GzipFile
from  io import BytesIO
from time import sleep
#from threading import Thread
from multiprocessing import Process


url = "http://127.0.0.1:8000/"
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
    print(f"response : {r.text}")

def ReadAndSendTorrent(hash):
    torrent = o(filesquery.format(hash)).read().decode()
    if (torrent!=""):
        Resp("settorrentdata", SetData(torrent = torrent, hash = hash))

def ParseTorrents(torrents):
    for torrent in torrents:
        if "hash" in torrent:
            hash = torrent['hash']
            ReadAndSendTorrent(hash)

def IsDownloading(torrent:dict):
    try:
        return torrent.get('state','unk') == 'downloading'
    except:
        pass
    
def ExecuteSubProcesses():
    print("executing subprocesses")
    processes =  [
        Popen(["python3",__file__,"global"]),
        Popen(["python3",__file__,"downloading"]),
        Popen(["python3",__file__,"otherstates"]),
    ]
    try:
        while True:
            pass
    except KeyboardInterrupt:
        for process in processes:
            print(f"killing process : {process.args[2]}")
            process.kill()

def data():
    return j.loads(data_str())

def data_str():
    return o(globalquery).read()

def SendGlobal():
    try:
        def GetDict(line):
            return dict([pair for pair in list(line.items()) if pair[0] in AcceptedFields])

        AcceptedFields =[
            "hash",
            "name",
            "size",
            "progress",
            "state",
            ]

        print("sending global")
        while True:
            d = data()
            simplified = j.dumps([GetDict(line) for line in d])
            Resp("setdata/",SetData(data = simplified))
    except KeyboardInterrupt:
        pass

def SendFiles(onlyDownloading:bool):
    try:
        print(f"sendig files, Downloading only={onlyDownloading}")
        while True:
            loaded = data()
            downloading = [torrent for torrent in loaded if IsDownloading(torrent)]

            for torrent in downloading:
                loaded.remove(torrent)
            if onlyDownloading:
                ParseTorrents(downloading)
            else:
                ParseTorrents(loaded)
    except KeyboardInterrupt:
        pass
        
def main(argc,argv):
    
    if argc != 2:
        ExecuteSubProcesses()
    elif argv[1]=="global":
        SendGlobal()
    elif argv[1]=="downloading":
        SendFiles(True)
    elif argv[1]=="otherstates":
        SendFiles(False)

   
     

if __name__ == "__main__":
    main(len(sys.argv),sys.argv)