import json as j

def dump(data):
    content = ""
    try:
        parsed  = j.loads(data)
        content = '<table style="width:100%"><tr><th>Name</th><th>Size</th><th>Progress</th><th>State</th></tr>'
        if isinstance(parsed,list):
            for line in parsed:
                if isinstance(line,dict):
                    size,unit = GetSize(line['size'])
                    content += (f"<tr><td><a href='/files?hash={line['hash']}'>{line['name']}</a></td><td>{size:0.2f}{unit}</td><td>{line['progress']*100:.2f}</td><td>{line['state']}</td></tr>")
            content +="</table>"
    except:
        pass
    return content

def dumpfiles(data):
    content = ""
    #try:
    parsed = j.loads(data)
    content = '<table style="width:100%"><tr><th>Name</th><th>Size</th><th>Progress</th></tr>'
    if isinstance(parsed,list):
        for line in parsed:
            if isinstance(line,dict):
                size,unit = GetSize(line['size'])
                content += (f"<tr><td>{line['name']}</td><td>{size:0.2f}{unit}</td><td>{line['progress']*100:.2f}</td></tr>")
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