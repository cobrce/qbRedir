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
        self.connected = False

    def connect(self):
        self.accept()
        
        if self.add_to_dictionary():
            response_dict = self.success_connection_dict
            self.connected = True
        else:
            response_dict = self.failed_connection_dict
        self.send(j.dumps(response_dict))

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
            else:
                self.default_command()
        except:
            self.default_command()
    
    def default_command(self):
        self.send("")

    def get_destination(self,loaded:dict):
        if "dest" in loaded and loaded["dest"] in self.destination_dictionary:
            return self.destination_dictionary[loaded["dest"]]
        else:
            return None

    def __str__(self):
        return self.name

    @property
    def success_connection_dict(self):
        return{
            "status":"connected",
            "name" : self.name,
            "type" : self.connection_type,
        }

    @property
    def failed_connection_dict(self):
        return {
            "status":"not connected",
        }

    @property
    def session_dictionary(self):
        raise NotImplementedError
    
    @property
    def destination_dictionary(self):
        raise NotImplementedError

    #either client or server
    @property
    def connection_type(self):
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
    
    @property
    def connection_type(self):
        return "server"
            

class Client(Consumer):
    @property
    def session_dictionary(self):
        return clients

    @property
    def destination_dictionary(self):
        return servers

    @property
    def connection_type(self):
        return "client"

    @property
    def success_connection_dict(self):
        return {
            **super().success_connection_dict,
            **self.servers_list_as_dict,
        }
    
    @property
    def servers_list_as_dict(self):
        return {
            "servers" : list(servers.keys()),
        }

    def default_command(self):
        self.send(text_data=j.dumps(self.success_connection_dict))

    