import json as j
from websocket import create_connection
from threading import Thread
from time import sleep
from urllib.request import urlopen as o
import re

torrents_url = r"http://127.0.0.1:8080/query/torrents"
files_url = r"http://127.0.0.1:8080/query/propertiesFiles/{}"

def client_def():
    sleep(1)
    ws = create_connection(client_url)
    data = ws.recv()
    print(data)

    try:
        loaded = j.loads(data)
        if "servers" in loaded:
            servers = loaded["servers"]
            if len(servers)!= 0:
                server_name = servers[0]
                print(f"using first server : {server_name}")
            else:
                print("no server connected")
        else:
            print("invalid dictionary response")
            return
    except:
        print("invalid json response")
        return

    
    while True:
        try:
            data = ws.recv()
            # the outer json contains the server/cleint communication data
            # the inner json (data) contains sent strings, therefore the server won't deserialize it
            loaded =j.loads(j.loads(data)["data"])
            try:
                for line in loaded:
                    print(f"{line['progress']:.2f}\t\t{line['size']}\t\t{line['name']}")
                
                line0 = loaded[0]
                if "hash" in line0:
                    hash = line0["hash"]
                    print(f"\nRequesting list of files for {hash}\n")

                    ws.send(j.dumps({
                        "dest" : server_name,
                        "url" : files_url.format(hash),
                    }))
            except:
                pass
        except KeyboardInterrupt:
            return
        except:
            pass

def tryexcept(method):
    def _register(*args,**kwargs):
        try:
            return method(*args,**kwargs)
        except Exception as e:
            print(e)
    return _register


class Client:    

    def __init__(self):
        self.client_name = "PrimeClient"
        self.client_url = f"ws://127.0.0.1:8000/client/{self.client_name}"
        self.ws = None
        self.servers = list()
        self.torrents = list()
        self.server = ""
        self.connect()
    

    @tryexcept
    def list_of_server(self):
        self.ws.send("")
        loaded = j.loads(self.ws.recv())
        self.servers = loaded["servers"]
        return self.servers
    
    @staticmethod
    def GetSize(size):
        units = ['B','Kib','Mib','Gib','Tib']
        unit = 0
        while size > 1024 and unit < len(units):
            size /= 1024
            unit +=1
        return size, units[unit]
        
    def listoftorrents(self):
        if self.server:
            print("\nRequesting list of torrents\n")
            self.ws.send(j.dumps({
                "dest" : self.server,
                "url" : torrents_url,
                })
            )
            data = self.ws.recv()
            loaded =j.loads(j.loads(data)["data"])
            try:
                print (" index\tprogress\t          size\t        name")
                index = 0
                self.torrents.clear()
                for line in loaded:
                    self.torrents.append({
                        "name" : line['name'],
                        "hash" : line['hash'],
                        }
                    )
                    size,unit = self.GetSize(line['size'])
                    print(f" {index:05}\t{line['progress']:8.2f}\t{size:10.2f} {unit}\t{line['name']}")
                    index+=1
            except:
                pass
                
        else:
            print("No server selected")
        pass
    def listoffiles(self,hash:str ="",index:int=None):
        pass

    def connect(self):
        if self.ws is not None:
            self.ws.close()
        self.ws = create_connection(self.client_url)
        data = self.ws.recv()
        try:
            loaded = j.loads(data)
            status = loaded.get('status')
            if status == "connected":
                print(f"connected as :{loaded.get('name')}")
            else:
                print(f"status : {status}")
        except:
            print("invalid json response")
            return

def help(*args,**kwargs):
    print("""
Available commands :
help : display this message
reconnect : connect as client (should be called first)
servers : display list of servers
server <index> / server <name> [--f] : select server by index/name [--f to force set server name]
torrents : display list of torrents of selered server
torrent <index>/<part of name> : select a torrent by index/part of name
update : update status of selected torrent
files : display list of files selected torrent
q : quit
""")    

@tryexcept
def reconnect(*args,**kwargs):
    global client
    client.connect()

@tryexcept
def servers(*args,**kwargs):
    global client
    print(client.list_of_server())

@tryexcept
def selectserver(*args,**kwargs):
    global client
    name = kwargs.get("name")
    if name:
        if name in client.server or "force" in kwargs:
            client.server = name
            print(f"{client.server} selected")
        else:
            print("server not found, use --f parameter to force select")
    else:
        index = kwargs.get("index")
        if index:
            index = int(index)
            if (index < len(client.servers)):
                client.server = client.servers[index]
                print(f"{client.server} selected")
            else:
                print("Index out of range")
        else:
            print("No enough parameters, server not selected")

@tryexcept
def torrents(*args,**kwargs):
    global client
    client.listoftorrents()

commands = {
    r"^q$" : exit,
    r"^help$" : help,
    r"^reconnect$" : reconnect,
    r"^servers$" : servers,
    r"^server\s+((?P<name>[a-z]+)|(?P<index>[\d]+))(\s+(?P<force>--f))?$" : selectserver,
    r"^torrents$" : torrents,
}

client = None

def main():
    global client
    client = Client()
    help()
    while True:
        try:
            command = input()
            if command:
                for pattern,handler in commands.items():
                    match = re.match(pattern,command,re.IGNORECASE)
                    if match:
                        handler(**match.groupdict())
                        break
                else:
                    print("invalid command")
        except:
            break

if __name__ =="__main__":
    main()
