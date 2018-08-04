import json as j
from websocket import create_connection
from threading import Thread
from time import sleep
from urllib.request import urlopen as o
import re
from datetime import timedelta
torrents_url = r"http://127.0.0.1:8080/query/torrents"
files_url = r"http://127.0.0.1:8080/query/propertiesFiles/{}"
general_url= r"http://127.0.0.1:8080/query/propertiesGeneral/{}"

def tryexcept(method):
    def _register(*args,**kwargs):
        try:
            return method(*args,**kwargs)
        except Exception as e:
            print(repr(e))
    return _register

def solvehash(function):
    def _register(self,hash:str ="",index:int=None):
        if hash is None:
            if index is None:
                print("No enough parameteres")
                return
            elif len(self.torrents)<index:
                print("Index out of range")
                return
            else:
                hash = self.torrents[index]["hash"]
        return function(self,hash=hash)
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
                 

    def listoftorrents(self):
        print("\nRequesting list of torrents\n")
        self.torrents = self.send_url(torrents_url)
        return self.torrents

    @solvehash
    def torrent_general(self,hash:str ="",index:int=None):
        print("\nRequesting torrent's general properties\n")
        return self.send_url(general_url.format(hash))

    @solvehash
    def listoffiles(self,hash:str ="",index:int=None):
        print("\nRequesting torrent's files\n")
        return self.send_url(files_url.format(hash))

    def send_url(self,url):
        if self.server:
            self.send({
                "dest" : self.server,
                "url" : url,
                }
            )

            error,loaded = self.recv()
            if not error:
                try:
                    # extract data
                    loaded =j.loads(loaded["data"])
                except KeyError:
                    # extraction error
                    print("Data not found")
                    return
                return loaded
            else:
                print(error)                
        else:
            print("No server selected")
    
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
        self.torrent = None
        self.commands = {
            r"^(q|quit|exit)$" : exit,
            r"^help$" : self.list_of_commands,
            r"^reconnect$" : self.reconnect,
            r"^servers$" : self.servers,
            r"^server(\s+((?P<index>[\d]+)|(?P<name>.+?))(\s+(?P<force>--f))?)?$" : self.selectserver,
            r"^torrents$" : self.torrents,
            r"^filter\s+(?P<beginning>.+)$" : self.filter,
            r"^torrent(\s+((?P<index>[\d]+)|(?P<beginning>.+)))?$" : self.selecttorrent,
            r"^update$" : self.update,
        }

    def loop(self):
        self.list_of_commands()
        while True:
            try:
                command = input().strip()
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
        server : display selected server
        torrents : display list of torrents of selered server
        torrent <index>/<beginning of name> : select a torrent by index/part of name 
        torrent : display selected torrent
        filter <string> : display torrents lines that contains <string>
        update : update status of selected torrent
        files : display list of files selected torrent
        q / exit / quit: quit
    """)    

    @tryexcept
    def reconnect(self,*args,**kwargs):
        self.client.connect()

    @tryexcept
    def servers(self,*args,**kwargs):
        servers = self.client.list_of_server()
        print("\n".join([" ".join([f"{i:4}",servers[i]]) for i in range(len(servers) )]))

    @tryexcept
    def selectserver(self,*args,**kwargs):
        def printselected():
            if self.client.server:
                print(f"Selected : {self.client.server}")
            else:
                print("No server selected")
        
        name = kwargs.get("name")
        if name:
            if name in self.client.servers or kwargs.get("force"):
                self.client.server = name
                printselected()
            else:
                print("server not found, use --f parameter to force select")
        else:
            index = kwargs.get("index")
            if index:
                index = int(index)
                if (index < len(self.client.servers)):
                    self.client.server = self.client.servers[index]
                    printselected()
                else:
                    print("Index out of range")
            else:
                printselected()

    @tryexcept
    def filter_torrents(self,beginning):
        filtered = list()
        indexes = list()
        index = 0
        for torrent in self.client.torrents:
            if torrent["name"].lower().startswith(beginning.lower()):
                filtered.append(torrent)
                indexes.append(index)
            index+=1
        return filtered,indexes
                
    
    @tryexcept
    def selecttorrent(self,*args,**kwargs):
        def printselected():
            name = ""
            if self.torrent:
                name = self.torrent.get('name')
            if name:
                print (f"Selected : {name}")
            else:
                print("No torrent selected")

        beginning = kwargs.get("beginning")
        if beginning:
            filtered,_ = self.filter_torrents(beginning)
            if len(filtered) > 0:
                self.torrent = filtered[0]
                printselected()
            else:
                print("No torrent found")
        else:
            index = kwargs.get("index")
            if index:
                index = int(index)
                if index < len( self.client.torrents):
                    self.torrent = self.client.torrents[index]                        
                    printselected()
                else:
                    print("Index out of range")
            else:
                printselected()


    @tryexcept
    def torrents(self,*args,**kwargs):
        torrents = self.client.listoftorrents()
        if torrents:
            self.torrents_table = self.format_torrents_table_dict(torrents)            
            self.display_torrents_table_dict(self.torrents_table)
    
    @tryexcept
    def filter(self,*args,**kwargs):
        beginning = kwargs.get("beginning")
        if beginning:
            self.display_torrents_table_dict(
                self.torrents_table,
                lambda x: beginning.lower() in x.lower()
            )
        else:
            print("No enough parameters")

    @staticmethod
    def getstate(state):
            states ={
                "downlo":"Downloading",
                "paused":"Paused",
                "queued":"Queued",
            }
            return states.get(state[:6],'Unknown')

    @tryexcept
    def update(self,*args,**kwargs):

        def sizeformat(size):
            hsize,unit =  self.GetSize(size)
            return f"{hsize:.2f} {unit}"

        fields_n_handlers ={
            "state" : lambda x : f"State : {self.getstate(x)}",
            "dl_speed" : lambda x : f"Download speed : {sizeformat(x)}/s",
            "up_speed" : lambda x : f"Upload speed :  {sizeformat(x)}",
            "progress" : lambda x : f"Progress {x*100:.2f}",
            "total_size": lambda x : f"Size :  {sizeformat(x)}",
            "total_downloaded" : lambda x : f"Downloaded {sizeformat(x)}",
            "eta" : lambda x : f"ETA : {str(timedelta(x))}",
            "seeds" : lambda x : f"Seeds : {x}",
            "save_path" : lambda x : f"Path : {x}",
            "category" : lambda x : f"Category : {x}",
        }
        if self.torrent:
            if "hash" in self.torrent:
                general = self.client.torrent_general(hash = self.torrent["hash"])
                for field,handler in fields_n_handlers.items():
                    if field in general:
                        value = general.get(field)
                    elif field in self.torrent:
                        value = self.torrent.get(field)
                    else:
                        continue
                    print(handler(value))
            else:
                print("Can't find 'hash' in torrent")
        else:
            print("No torrent selected")
            

    @staticmethod
    def GetSize(size):
        units = ['B','Kib','Mib','Gib','Tib']
        unit = 0
        while size > 1024 and unit < len(units):
            size /= 1024
            unit +=1
        return size, units[unit]

    @staticmethod
    def display_torrents_table_dict(table:dict,condition = lambda x:True):
        print(table.get("header"))
        for index in table:
            if index!="header":
                if condition(table[index]):
                    print(table[index])
    
    @staticmethod
    def format_torrents_table_dict(torrents : list) -> dict:
        table = {
            "header" :f" index progress {'state':11} {'size':10}         name",
        }
        i = 0
        for line in torrents:
            size,unit = main.GetSize(line['size'])
            table[i] = f" {i:05} {line['progress']:8.2f} {main.getstate(line['state']):11}  {size:10.2f} {unit}  {line['name']}"
            i+=1

        return table

if __name__ =="__main__":
    main().loop()