from setter import *
import json as j
from websocket import create_connection

class Server:
    def __init__(self,address:str):
        self.ws = create_connection(address)
        pass

    def Send(self,data):        
        if type(data) is str:
            message = data
            self.ws.send(data)        
        elif type(data) is dict:
            message =  j.dumps(data)
        else:
            raise TypeError()
        self.ws.send(message)   

server = Server("ws://127.0.0.1:8000/server/")
