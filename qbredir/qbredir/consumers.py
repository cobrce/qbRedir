from channels.sessions import channel_session
from channels.message import Message
from channels import Group
import json as j
import re


## the client send url
## the server executes it the send results

def matchType(string):
    typepattern = r"^(\/)?(?P<type>[\w]*)(\/)?$"
    m = re.match(typepattern,string)
    if m is not None:
        return m.groupdict().get('type')
    else:
        return None

def isServer(path:str):
    return matchType(path) == "server"

def isClient(path:str):
    return matchType(path) == "client"

@channel_session
def ws_connect(message:Message):
    if 'path' in message:
        connectionType = matchType(message['path'].decode())
        if connectionType in ["server","client"]:
            Group("server")
    
    pass

@channel_session
def ws_receive(message:Message):

    pass

@channel_session
def ws_disconnect(message:Message):
    pass

# def ws_connect(message:Message):
#     message.channel_session['path'] =message['path'].decode()

#     Group('clients').add(message.reply_channel)

# @channel_session
# def ws_receive(message:Message):
#     # print(f"message.content['text'] = {message.content['text']}")
#     json = message.content['text']
#     try:
#         deserialized = j.loads(json)
#         path = message.channel_session['path'] 
#         if path == "set":
#             Set(deserialized)
#         elif path == "get":
#             Get(deserialized)
#     except:
#         response = "error"
#     else:
#         response = "ok"
#     Group('clients').send({"text":response})
    
# @channel_session
# def Set(deserialized):
#     if "global" in deserialized:
#             for torrent in deserialized["global"]:
#                 try:
#                     if "hash" in torrent:
#                         # print(torrent['hash'])
#                         Group('clients').send({"text" : j.dumps({"hash" : torrent["hash"]})})
#                 except:
#                     print(torrent)
#         # elif "torrent" in data and "hash" in data:
#         #     hash = data['hash']
#         #     torrent = data["torrent"]
#         #     Group('clients').send({"text":"ok"})

# @channel_session
# def Get(deserialized):
#     pass

# @channel_session
# def ws_disconnect(message:Message):
#     Group('clients').discard(message.reply_channel)