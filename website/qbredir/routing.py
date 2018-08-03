from channels.routing import ProtocolTypeRouter,URLRouter
from channels.auth import AuthMiddlewareStack

from django.conf.urls import url
from qbredir.consumers import Server,Client

websocket_urlpattern = [
    url(r'^server/(?P<name>[^/]+)$',Server),
    url(r'^client/(?P<name>[^/]+)$',Client),
]

# protocol routing
application = ProtocolTypeRouter(
    {
        # (http->django views is added by default)
        "websocket" : AuthMiddlewareStack(
            URLRouter(
                websocket_urlpattern
            )
        ),
    }
)


