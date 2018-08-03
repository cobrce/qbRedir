import json as j
from websocket import create_connection
from urllib.request import urlopen as o
import sys
from threading import Thread
import re

class Config:
    server_url = "ws://127.0.0.1:8000/server/Prime"
    qb_url = "http://127.0.0.1:8080"

class Server:
    def __init__(self,config:Config):
        self.config = config
        self.create_connection()
        self.running = True
        self.thread = Thread(target=self.loop)
        self.thread.start()

    def create_connection(self):
        self.ws = create_connection(self.config.server_url)

    def pause(self):
        self.running = False
    
    def reusme(self):
        self.running = True

    def loop(self):
        try:
            while True:
                if self.running:
                    data = self.ws.recv()
                    try:
                        loaded = j.loads(data)
                        # download data from "url" and send it in a dictionary {"data" : data, "client" : client}
                        if "url" in loaded and "client" in loaded:
                            url = self.extracturl(loaded['url'])                        
                            resp = o(url).read().decode()
                            self.send(j.dumps({
                                "client" : loaded["client"],
                                "data" : resp
                            }))
                    except:
                        pass
        except:
            pass

    def extracturl(self,url:str):
        pattern = "^http(s)?://(?P<link>[^$]*)$"
        match = re.match(pattern,url)
        if match is not None:
            if match["link"] !="":
                return url

        else:
            if not url.startswith("/"):
                url = "/" + url
            return self.config.qb_url + url

    def send(self,data):        
        if type(data) is str:
            message = data
            self.ws.send(data)        
        elif type(data) is dict:
            message =  j.dumps(data)
        else:
            raise TypeError()
        self.ws.send(message)

    def recv(self):
        return self.ws.recv()   

server = Server(Config())
try:
    while True:
        print(server.recv())
except:
    pass
