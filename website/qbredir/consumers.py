import json as j
import re
from channels.generic.websocket import WebsocketConsumer
import random

servers = dict()
clients = dict()

class Consumer(WebsocketConsumer):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = ""

    def connect(self):
        self.accept()

    def receive(self,text_data):
        try:
            loaded = j.loads(text_data)
            # check if the destination is provided and connected
            destination = self.get_destination(loaded)
            if destination is not None:
                # adjust the dictionary and send it
                loaded["src"] = self.name
                destination.send(text_data = j.dumps(loaded))
                print(f"sent from {self.name} to {destination}")
        except:
            pass
    
    def get_destination(self,loaded:dict):
        if "dest" in loaded and loaded["dest"] in self.destination_dictionary:
            return self.destination_dictionary[loaded["dest"]]
        else:
            return None

    def __str__(self):
        return self.name
    @property
    def session_dictionary(self):
        raise NotImplementedError
    
    @property
    def destination_dictionary(self):
        raise NotImplementedError

    def add_to_dictionary(self):
        name = self.scope['url_route']['kwargs'].get('name')
        if name !="":
            self.name = self.uniquename(name)            
            self.session_dictionary[self.name] = self
            return True
        else:
            return False 

    def disconnect(self,close_code):
        if self.name in servers:
            del servers[self.name]

    def uniquename(self,name:str):
        if name in servers:
            index = 1
            while name +str(index) in servers:
                index+=1
            name = name+str(index)

        return name

class Server(Consumer):
    @property
    def session_dictionary(self):   
        return servers
    
    @property
    def destination_dictionary(self):
        return clients
      
    def connect(self):
        super().connect()
        if self.add_to_dictionary():
            self.send(text_data=f"server connected as : {self.name}")
        else:
            self.send(text_data="server not connection : name not provided")

class Client(Consumer):
    @property
    def session_dictionary(self):
        return clients

    @property
    def destination_dictionary(self):
        return servers   

    def connect(self):
        super().connect()
        if self.add_to_dictionary():
            self.send(text_data=f"client connected as : {self.name}")
            self.send(text_data=self.display_servers_message)
        else:
            self.send(text_data="client not connection : name not provided")
    
    @property
    def display_servers_message(self):
        message ="available servers :"
        for key in servers.keys():
            message += "\n" + key
        pass
        return message
    