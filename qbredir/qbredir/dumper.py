import json as j
states ={
        "downlo":"Green",
        "paused":"Orange",
        "queued":"Blue",
        "stalle":"Black"
        }
states_full = {
                "downlo" : "downloading",
                "paused" : "paused",
                "stalle" : "stalled",
                "queued" : "queued",
                "unknown" : "unknown"
              }

header ="""<html>
    <header>
    <style>
    table, th, td {
    border: 1px solid black;
    border-collapse: collapse;
    }

    tr:nth-child(even) {
    background-color: #eee;
    }

    tr:nth-child(odd) {
    background-color: #fff;
    }

    th {
    color: white;
    background-color: black;
    }

    </style>
    </header>"""

def dump(data):
    content = ""
    #try:
    parsed = sorted(j.loads(data), key = lambda k:CompareDict(k))
    content =header + '<table border="1" style="width:100%"><tr><th>Name</th><th>Size</th><th>Progress</th><th>State</th></tr>'
    if isinstance(parsed,list):
        for line in parsed:
            if isinstance(line,dict):
                size,unit = GetSize(line['size'])
                index, color,state =ExtractState(line['state'])
                state = states_full[state]
                content += (f"<tr><td><a href='/files?hash={line['hash']}'>{line['name']}</a></td><td>{size:0.2f}{unit}</td><td>{line['progress']*100:.2f}%</td><td><font color={color}>{state}</font></td></tr>")
        content +="</table>"
    #except:
    #    pass
    return content
def CompareDict(dict):
    if 'state' in dict:
        state = dict['state']
        index, color,_ = ExtractState(state)
        if index is not None:
            return index
    return len(states)

def ExtractState(state):
    if len(state)>5:
        state = state[:6]
        if state in states:
            return list(states.keys()).index(state), states[state],state
    return None,"Gray","unknown"

def dumpfiles(data):
    content = ""
    #try:
    parsed = j.loads(data)
    content = header + """<table style="width:100%"><tr><th>Name</th><th>Size</th><th>Progress</th></tr>"""
    if isinstance(parsed,list):
        for line in parsed:
            if isinstance(line,dict):
                size,unit = GetSize(line['size'])
                content += (f"<tr><td>{line['name']}</td><td>{size:0.2f}{unit}</td><td>{line['progress']*100:.2f}%</td></tr>")
        content +="</table>"
    #except:
    #    pass
    return content

def GetSize(size):
    units = ['B','Kib','Mib','Gib','Tib']
    unit = 0
    while size > 1024 and unit < len(units):
        size /= 1024
        unit +=1
    return size, units[unit]