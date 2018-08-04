import json as j
from websocket import create_connection
from urllib.request import urlopen as o
import sys
from threading import Thread
import re

server_name = "PrimeServer"
server_url = f"ws://127.0.0.1:8000/server/{server_name}"

def server():
    try:
        ws = create_connection(server_url)
        loaded = j.loads(ws.recv())
        if loaded["status"] == "connected":
            name = loaded['name']
            print(f"connected as {name}")
        else:
            print("could not connect")
            return
    except:
        print ("error occured, server stopped")
        return
    
    while True:
        try:
            data =  ws.recv() # waiting for commands
            print(data) # printing command
            loaded  = j.loads(data)
            # source will be destination
            if "src" in loaded:
                loaded["dest"],loaded["src"] = loaded["src"],loaded["dest"]
                if "url" in loaded:
                    try:
                        loaded["data"] =  o(loaded["url"]).read().decode()
                        print(f"sending from {loaded['src']} to {loaded['dest']}")
                        ws.send(j.dumps(loaded))
                    except Exception as e:
                        print(e)
        except KeyboardInterrupt:
            return
        except:
            pass

Thread(target=server,daemon=True).start()

while True:
    try:
        input() # because normal ctrl-c is not working while recv is running
    except:
        break