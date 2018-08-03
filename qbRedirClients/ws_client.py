import json as j
from websocket import create_connection
from threading import Thread
from time import sleep
from urllib.request import urlopen as o

client_url = "ws://127.0.0.1:8000/client/Primeclient"
server_url = "ws://127.0.0.1:8000/server/Primeserver"
torrents_url = r"http://127.0.0.1:8080/query/torrents"

def client():
    sleep(1)
    ws = create_connection(client_url)
    print (ws.recv()) # send rcommand
    ws.send(j.dumps({
        "dest" : "Primeserver",
        "url" : torrents_url,
        })
    )
    while True:
        try:
            data = ws.recv()
            # the outer json contains the server/cleint communication data
            # the inner json (data) contains sent strings, therefore the server won't deserialize it
            loaded =j.loads(j.loads(data)["data"])
            for line in loaded:
                print(f"{line['progress']:.2f}\t\t{line['name']}")
        except KeyboardInterrupt:
            return
        except:
            pass


def server():
    ws = create_connection(server_url)
    while True:
        try:
            data =  ws.recv() # waiting for commands
            print(data) # printing command
            loaded  = j.loads(data)
            # source will be destination
            if "src" in loaded:
                loaded["dest"],loaded["src"] = loaded["src"],loaded["dest"]
                if "url" in loaded:
                    loaded["data"] =  o(loaded["url"]).read().decode()
                    ws.send(j.dumps(loaded))
        except KeyboardInterrupt:
            return
        except:
            pass


Thread(target=server,daemon=True).start()
Thread(target=client,daemon=True).start()

while True:
    try:
        pass
    except KeyboardInterrupt:
        break


