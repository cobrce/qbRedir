import json as j

def dump(data):
    content = ""
    try:
        parsed  = j.loads(data)
        content = '<table style="width:100%"><tr><th>Name</th><th>Progress</th><th>State</th></tr>'
        if isinstance(parsed,list):
            for line in parsed:
                if isinstance(line,dict):
                    content += (f"<tr><td><a href='/files?hash={line['hash']}'>{line['name']}</a></td><td>{line['progress']}</td><td>{line['state']}</td></tr>")
            content +="</table>"
    except:
        pass
    return content

def dumpfiles(data):
    content = ""
    content = "data"
    return content
    try:
        parsed = j.loads(data)
        content = '<table style="width:100%"><tr><th>Name</th><th>Size</th><th>Progress</th></tr>'
        if isinstance(parsed,list):
            for line in parsed:
                if isinstance(line,dict):
                    content += (f"<tr><td>{line['name']}</td><td>{line['size']}</td><td>{line['progress']}</td></tr>")
            content +="</table>"
    except:
        pass
    return content
