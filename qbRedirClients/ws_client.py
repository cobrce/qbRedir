import json as j
from websocket import create_connection
from threading import Thread
from time import sleep
from urllib.request import urlopen as o
import re
from datetime import timedelta
from msvcrt import kbhit as getch


qbitorrent_webui = "http://127.0.0.1:8080"
website = "ws://127.0.0.1:8000"
clientName = "PrimeClient"


torrents_url = f"{qbitorrent_webui}/query/torrents?sort=state"
hash_filter = r"&hashes={}"
files_url = f"{qbitorrent_webui}/query/propertiesFiles/{{}}"
general_url= f"{qbitorrent_webui}/query/propertiesGeneral/{{}}"

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
    def __init__(self,client_name,autoreconnect = True):
        self.client_name = client_name
        self.client_url = f"{website}/client/{self.client_name}"
        self.ws = None
        self.autoreconnect = autoreconnect
        self.servers = list()
        self.torrents = list()
        self.server = ""
        self.connect()
    
    @property
    def allowed_sources(self):
        return ["host",self.server]

    def recv(self):
        while True:
            try:
                if self.ws:
                    loaded = j.loads(self.ws.recv())
                    if loaded.get("src") in self.allowed_sources:
                        break
                else:
                    raise ConnectionError
            except ConnectionError:
                return "Connection error, nothing received",{}
        
        return loaded.get("error"),loaded

    def _auto_reconnect(self,first_try):
        
        if self.autoreconnect:               
            if first_try:
                self.connect()
                first_try= False
                return True
                
            for i in range(5):
                print(f"Reconnecting in {5-i} seconds, press a key to abort")
                sleep(1)
                if getch():
                    print("Reconnection aborted")
                    return False # auto reconnect aborted by user
            self.connect()
            return True
        else:
            return False # auto reconnect disabled
    
    def send(self,message):
        if type(message) is not str:
            message = j.dumps(message)

        first_try = True        
        while True:
            try:
                if self.ws is None:
                    raise ConnectionError
                self.ws.send(message)
                return True
            except ConnectionError :
                if not self._auto_reconnect(first_try):
                    return False
                first_try = False
            except:
                pass

    @tryexcept
    def list_of_server(self):
        self.send("")
        error,loaded = self.recv()
        if not error:
            self.servers = loaded["servers"]
            return self.servers
        else:
            print(error)
            return {}
                 

    def listoftorrents(self,save:bool,hash:str=None):
        url = torrents_url
        if hash:
            url+=hash_filter.format(hash)
            print(f"Requesting update for {hash}")
        else:
            print("Requesting list of torrents")
        torrents = self.send_url(url)
        if save:
            self.torrents = torrents
        return torrents

    @solvehash
    def torrent_general(self,hash:str ="",index:int=None):
        print("Requesting torrent's general properties")
        return self.send_url(general_url.format(hash))

    @solvehash
    def listoffiles(self,hash:str ="",index:int=None):
        print("Requesting torrent's files")
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
            try:
                self.ws.close()
            except: # socket already closed excption
                pass
        try:
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
        except:
            print("Not connected, maybe server is down")

class main():

    def __init__(self):
        self.list_of_commands()
        self.client = Client(clientName)
        self.torrent = None
        self.torrents_table = list()
        self.commands = {
            r"^(q|quit|exit)$" : exit,
            r"^help$" : self.list_of_commands,
            r"^reconnect$" : self.reconnect,
            r"^servers$" : self.servers,
            r"^server(\s+((?P<index>[\d]+)|(?P<name>.+?))(\s+(?P<force>-f))?)?$" : self.selectserver,
            r"^torrents(((\s+)(?P<cached>-c))|((\s+)(?P<silent>-s)))?$" : self.torrents,
            r"^(?P<mode>t|f)filter\s+(?P<string>.+)$" : self.filter,
            r"^torrent(\s+((?P<index>[\d]+)|(?P<beginning>.+)))?$" : self.selecttorrent,
            r"^update$" : self.update,
            r"^files(((\s+)(?P<cached>-c))|((\s+)(?P<silent>-s)))?$" : self.files,
        }

    def loop(self):
        while True:
            try:
                prompt = ""
                if self.client.server:
                    prompt = f"({self.client.server})"
                if self.torrent:
                    prompt+= f".({self.torrent.get('name')})"
                prompt +="$ "

                command = input(prompt).strip()
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
        reconnect : reconnect the client (should be called first)
        servers : display list of servers
        server <index> / server <name> [-f] : select server by index/name
            "-f" to force set <server name>
        server : display selected server
        torrents [-c][-s]: retrieve and display the list of torrents of the selected server
            if "-s"used the list is not displayed
            if "-c" is used display cached list
            (the two parameter are mutually exlusive)
        torrent <index>/<beginning of name> : select a torrent by index or by beginning of name
        torrent : display selected torrent
        files [-c][-s] : retrieve list of files selected torrent
            if "-s"used the list is not displayed
            if "-c" is used display cached list
            (the two parameter are mutually exlusive)
        tfilter <string> : filter the table of torrents by showing only entries containing <string>
        ffilter <string> : filter the table of files by showing only entries containing <string>
        update : display the actual status of selected torrent
        q / exit / quit : quit
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

        if kwargs.get("cached") is None:
            self.torrents_table = self.format_torrents_table_dict(self.client.listoftorrents(True))
        else:
            print("<Cached mode>")
        if kwargs.get("silent") is None:
            if self.torrents_table:
                self.display_table(self.torrents_table)
            else:
                print("<No torrent to display")
        else:
            print("<Silent mode>")

    @tryexcept
    def files(self,*args,**kwargs):
        if self._hash_of_selected_torrent: # if there is any error message it's already printed by the property getter
                if kwargs.get("cached") is None:
                    # update
                    self.files_table_of_selected_torrent = self.format_files_table_dict(self.client.listoffiles(self._hash_of_selected_torrent))
                else:
                    print("<Cached mode>")

                if kwargs.get("silent") is None:
                    if self.files_table_of_selected_torrent:
                        self.display_table(self.files_table_of_selected_torrent)
                    else:
                        print("<No file to display>")
                else:
                    print("<Silent mode>")

    
    @tryexcept
    def filter(self,*args,**kwargs):
        mode_switcher = {
            "t" :(self.torrents_table,"<Table of torrents is empty>"),
            "f" :(self.files_table_of_selected_torrent,"<Table of files is empty>"),
        }
        string = kwargs.get("string")
        mode = kwargs.get("mode")

        if string and mode:
            table,errormessage =  mode_switcher[mode]

            if table and len(table)>0:
                self.display_table(
                    table,
                    lambda x: string.lower() in x.lower(),
                    True,
                    False
                )
            else:
                print(errormessage)
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

    @property
    def _hash_of_selected_torrent(self):
        if self.torrent:
            if "hash" in self.torrent:
                return self.torrent["hash"]
            else:
                print("Can't find 'hash' in torrent")
        else:
            print("No torrent selected")

    @tryexcept
    def update(self,*args,**kwargs):

        fields_n_handlers ={
            "state" : lambda x : f"State : {self.getstate(x)}",
            "dl_speed" : lambda x : f"Download speed : {self.sizeformat(x)}/s",
            "up_speed" : lambda x : f"Upload speed :  {self.sizeformat(x)}/s",
            "progress" : lambda x : f"Progress : {x*100:.2f}%",
            "total_size": lambda x : f"Size :  {self.sizeformat(x)}",
            "total_downloaded" : lambda x : f"Downloaded {self.sizeformat(x)}",
            "eta" : lambda x : f"ETA : {str(timedelta(seconds=x))}",
            "seeds" : lambda x : f"Seeds : {x}",
            "save_path" : lambda x : f"Path : {x}",
            "category" : lambda x : f"Category : {x}",
        }

        if self._hash_of_selected_torrent:
            general = self.client.torrent_general(hash = self._hash_of_selected_torrent)
            
            try:
                # try updating the torrent from the client
                torrent = self.client.listoftorrents(False,hash=self._hash_of_selected_torrent)[0]
            except:
                # use the current value
                torrent = self.torrent

            for field,handler in fields_n_handlers.items():
                if field in general:
                    value = general.get(field)
                elif field in torrent:
                    value = torrent.get(field)
                else:
                    continue
                print(handler(value))
    
    @property
    def files_table_of_selected_torrent(self):
        if self.torrent and "files" in self.torrent:
            return self.torrent["files"]
    
    @files_table_of_selected_torrent.setter
    def files_table_of_selected_torrent(self,table):
        if self.torrent:
            self.torrent["files"] = table

    @staticmethod
    def GetSize(size):
        units = ['B','Kib','Mib','Gib','Tib']
        unit = 0
        while size > 1024 and unit < len(units):
            size /= 1024
            unit +=1
        return size, units[unit]

    @staticmethod
    def display_table(table:dict,condition = lambda x:True,print_header=True,print_footer = True):
        # header
        if print_header and  "header" in table:
            print(table.get("header"))
        # content
        for index in table:
            if index not in ["header","footer"]:
                if condition(table[index]): # filter content (default condiction is always True)
                    print(table[index])
        # footer
        if print_footer and "footer" in table:
            print(table.get("footer"))
    
    @staticmethod
    def format_torrents_table_dict(torrents : list) -> dict:
        def format_torrents_table_line(line:dict,index:int):
            return f" {index:05} {line['progress']*100:8.2f}% {main.getstate(line['state']):>11}  {main.sizeformat(line['size'])}  {line['name']}"

        if (torrents is None):
            print ("<No torrent>")
        else:
            return {
                "header" :f" index progress {'state':>11} {'size':>15}         name",
                **dict((i,format_torrents_table_line(torrents[i],i)) for i in range(len(torrents)))
            }

    @staticmethod
    def format_files_table_dict(files : list) -> dict:
        def format_file_line(line:dict,index:int):
            return f"Index : {index:04}\nName : {line['name']}\nSize : {main.sizeformat(line['size'])}\nProgress : {line['progress']*100:8.2f}%\nPriority : {line['priority']}\n"
        return {
            "footer" : f"Number of files : {len(files)}\n",
            **dict((i,format_file_line(files[i],i)) for i in range(len(files))),
        }

    @staticmethod
    def sizeformat(size):
            hsize,unit =  main.GetSize(size)
            return f"{hsize:10.2f} {unit:3}"

if __name__ =="__main__":
    main().loop()
