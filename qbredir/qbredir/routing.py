from channels.staticfiles import StaticFilesConsumer
from qbredir.consumers import *

channel_routing = {
'http.request' : StaticFilesConsumer(),
'websocket.connect' : ws_connect,
'websocket.receive' : ws_receive,
'websocket.disconnect' : ws_disconnect,
}