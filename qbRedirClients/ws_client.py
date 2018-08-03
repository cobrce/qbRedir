import json as j
from websocket import create_connection
from threading import Thread
from time import sleep
from urllib.request import urlopen as o

server_name = "PrimeServer"
client_name = "PrimeClient"

client_url = f"ws://127.0.0.1:8000/client/{client_name}"
server_url = f"ws://127.0.0.1:8000/server/{server_name}"
torrents_url = r"http://127.0.0.1:8080/query/torrents"
files_url = r"http://127.0.0.1:8080/query/propertiesFiles/{}"

def client():
    sleep(1)
    ws = create_connection(client_url)
    print (ws.recv()) # send rcommand
    ws.send(j.dumps({
        "dest" : server_name,
        "url" : torrents_url,
        })
    )
    while True:
        try:
            data = ws.recv()
            # the outer json contains the server/cleint communication data
            # the inner json (data) contains sent strings, therefore the server won't deserialize it
            loaded =j.loads(j.loads(data)["data"])
            try:
                for line in loaded:
                    print(f"{line['progress']:.2f}\t\t{line['size']}\t\t{line['name']}")
                
                line0 = loaded[0]
                if "hash" in line0:
                    hash = line0["hash"]
                    ws.send(j.dumps({
                        "dest" : server_name,
                        "url" : files_url.format(hash),
                    }))
            except:
                pass
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


