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
        self.send(response_dict)

    def receive(self,text_data):
        try:
            if text_data =="":
                self.default_command()
                return

            try:
                loaded = j.loads(text_data)
            except:
                self.send(self.invalid_json_message_dict)
                return
            
            destination = loaded.get("dest")
            if not destination:
                self.default_command()

            elif destination not in self.destination_dictionary:
                self.send({
                    "error" : "destination not connected"
                })

            else:
                # adjust the dictionary and send it
                loaded["src"] = self.name
                self.destination_dictionary[destination].send(text_data = j.dumps(loaded))
                print(f"sent from {self.name} to {destination}")

        except Exception as e:
            self.send(self.internal_error_message_dict)
            print(e)
            
    
    def send(self, text_data=None, bytes_data=None, close=False):
        if text_data is not None:
            if type(text_data) is not str:
                text_data = j.dumps(text_data)

        super().send(text_data=text_data,bytes_data=bytes_data,close=close)

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
    def invalid_json_message_dict(self):
        return {
            "error" : "invalid json format",            
        }

    @property
    def internal_error_message_dict(self):
        return{
            "error" : "Internal error"
        }

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
        if self.name in self.session_dictionary:
            del self.session_dictionary[self.name]

    def uniquename(self,name:str):
        if name in self.session_dictionary:
            index = 1
            while name +str(index) in self.session_dictionary:
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

    @property
    def invalid_json_message_dict(self):
        return{
            **super().invalid_json_message_dict,
            **self.servers_list_as_dict,
        }

    def default_command(self):
        self.send(self.success_connection_dict)

    