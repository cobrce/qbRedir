# qbRedir
qbRedir (qbittorrent redirection) is project that allows the remote access to qbittorent APIs even behind a router, the idea is creating a server (running in the same pc as qb) and a client (remotely executed) that both of them connect to a web-server that transfers their commands and the responses

## Requirements 
The whole project is written for python 3
The server and client need websocket-client module

`pip3 install websocket-client`

The website needs runs on django using channels for websocket, everything is in the requirements file

```
cd website
pip3 install -r requirements.txt
``` 

## Structure
The project is divided to three parts 
* **Server** : run in the same PC as qbittorent, this one connects to the website waiting for commands
* **Client** : this is the program that sends commands to the website
* **Website** : sends commands from client to server and response from server to client

### Server (ws_server.py)
Waits from the website the arival of json encoded dictionary having at least two keys : src and url, the first one is the source of the command (to replay to), the second is the url to be opened and have it content sent back to the client (through the website)

### Client (ws_client.py)
Many client-commands were implemented and most of them implies the server opening a url and send back it's content, which sent in a dictionary as a value of the key "data"

##### Client commands 
This is the list of client-commands to be entered in the client (not the actual ones sent to server)

* **help** : display the list of commands
* **reconnect** : reconnect the client
* **servers** : display list of servers
* **server \<index\> / \<server name\> [-f]** : select server by index or by name
    * -f to force set \<server name\>
* **server** : display selected server
* **torrents [-s]** : retrieve and display the list of torrents of the selected server
    * if "-s"used the list is not displayed
    * if "-c" is used display cached list
    * (the two parameter are mutually exlusive)
* **torrent \<index\>/\<beginning of name\>** : select a torrent by index or beginning of name
* **torrent** : display selected torrent
* **files [-s]** : retrieve list of files selected torrent
    * if "-s"used the list is not displayed
    * if "-c" is used display cached list
    * (the two parameter are mutually exlusive)
* **tfilter \<string\>** : filter the table of torrents by showing only entries containing \<string\>
* **ffilter \<string\>** : filter the table of files by showing only entries containing \<string\>
* **update** : display the actual status of selected torrent
* **q / exit / quit** : quit

The **tfilter** and **ffilter** commands use cached data

### Website
When a message (a json formatted dictionary) arrives from either the server or client it checks for the key "dest", if it's existing and matches a connected client or server, the website sends the dict to it (client or server) after adding the "src" key
The messages from servers are sent only to clients and vice versa.

##### Adding a server command
Actually the server support only the "url" command but anyone can be implemented, and this can be done without modifying the website since it cares only about the "dest" key

## Test (locally)
First update the **qbitorrent_webui** in **ws_client.py** to point to the address of qbittorent webui

It's preferable to use a virtual environment where you install the required modules

* First run the website
```
cd website
python manage.py runserver
```
*In case you set a specific address update the variable **website** in both **ws_server.py** and **ws_client.py***


* Run the server in another terminal
```
cd qbRedirClients
python ws_server.py
```

* Then the client in another terminal
```
cd qbRedirClients
python ws_client.py
```

***p.s** : this is my first django channel project, feel free to correct anything that seem wrong.*
