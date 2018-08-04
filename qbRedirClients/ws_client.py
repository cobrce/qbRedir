import json as j
from websocket import create_connection
from threading import Thread
from time import sleep
from urllib.request import urlopen as o
import re

torrents_url = r"http://127.0.0.1:8080/query/torrents"
files_url = r"http://127.0.0.1:8080/query/propertiesFiles/{}"

def tryexcept(method):
    def _register(*args,**kwargs):
        try:
            return method(*args,**kwargs)
        except Exception as e:
            print(repr(e))
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

    def recv(self):
        loaded = j.loads(self.ws.recv())
        return loaded.get("error"),loaded

    def send(self,message):
        if type(message) is not str:
            message = j.dumps(message)

        self.ws.send(message)

    @tryexcept
    def list_of_server(self):
        self.send("")
        error,loaded = self.recv()
        if not error:
            self.servers = loaded["servers"]
            return self.servers
        else:
            print(error)
        
    
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
            self.send({
                "dest" : self.server,
                "url" : torrents_url,
                }
            )

            error,loaded = self.recv()
            if not error:
                # extract data
                try:
                    loaded =j.loads(loaded["data"])
                except KeyError:
                    print("Data not found")
                    return
                # display data
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
                print(error)
                
        else:
            print("No server selected")

    def listoffiles(self,hash:str ="",index:int=None):
        pass

    def connect(self):
        if self.ws is not None:
            self.ws.close()
        self.ws = create_connection(self.client_url)
        error,loaded = self.recv()
        if not error:
            try:
                status = loaded.get('status')
                if status == "connected":
                    print(f"connected as :{loaded.get('name')}")
                else:
                    print(f"status : {status}")
            except:
                print("invalid json response")
                return
        else:
            print(error)
            print("Not connected, maybe server is down")

class main():

    def __init__(self):
        self.client = Client()
        self.commands = {
            r"^q$" : exit,
            r"^help$" : self.list_of_commands,
            r"^reconnect$" : self.reconnect,
            r"^servers$" : self.servers,
            r"^server\s+((?P<name>[a-z]+)|(?P<index>[\d]+))(\s+(?P<force>--f))?$" : self.selectserver,
            r"^torrents$" : self.torrents,
        }

    def loop(self):
        self.list_of_commands()
        while True:
            try:
                command = input()
                if command:
                    for pattern,handler in self.commands.items():
                        match = re.match(pattern,command,re.IGNORECASE)
                        if match:
                            handler(**match.groupdict())
                            break
                    else:
                        print("invalid command")
            except:
                break
    def list_of_commands(self,*args,**kwargs):
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
    def reconnect(self,*args,**kwargs):
        self.client.connect()

    @tryexcept
    def servers(self,*args,**kwargs):
        print(self.client.list_of_server())

    @tryexcept
    def selectserver(self,*args,**kwargs):
        name = kwargs.get("name")
        if name:
            if name in self.client.servers or kwargs.get("force"):
                self.client.server = name
                print(f"{self.client.server} selected")
            else:
                print("server not found, use --f parameter to force select")
        else:
            index = kwargs.get("index")
            if index:
                index = int(index)
                if (index < len(self.client.servers)):
                    self.client.server = self.client.servers[index]
                    print(f"{self.client.server} selected")
                else:
                    print("Index out of range")
            else:
                print("No enough parameters, server not selected")
    @tryexcept
    def torrents(self,*args,**kwargs):
        self.client.listoftorrents()

if __name__ =="__main__":
    main().loop()
