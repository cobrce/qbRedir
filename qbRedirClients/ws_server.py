import json as j
from websocket import create_connection
from urllib.request import urlopen as o
from threading import Thread
from time import sleep

server_name = "PrimeServer"
website = "ws://127.0.0.1:8000"

server_url = f"{website}/server/{server_name}"

def connect():
    while True:
        print (f"connecting to {server_url}")
        try:
            ws = create_connection(server_url)
            loaded = j.loads(ws.recv())
            if loaded["status"] == "connected":
                name = loaded['name']
                print(f"connected as {name}")
                return ws
            else:
                print("could not connect")
        except:
            print ("error occured, server stopped")
        for i in range(5):
            print(f"retry in {5-i} seconds")
            sleep(1)
            

def server():
    ws = None
    while True:
        try:
            if ws is None:
                ws = connect()
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
        except ConnectionError:
            ws.close()
            ws = None
        except Exception as e:
            pass

Thread(target=server,daemon=True).start()

while True:
    try:
        input() # because normal ctrl-c is not working while recv is running
    except:
        break