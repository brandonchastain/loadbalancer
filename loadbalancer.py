from bottle import route, run, request, response, redirect
import requests
import configparser
from urllib.parse import urlparse

serverlist = None
currentServer = 0
srcIpMap = dict()

@route('/', method=['GET', 'POST'])
@route('/<p:path>', method=['GET', 'POST'])
def index(p=""):
    method = request.method
    body = request.body.read()
    headers = dict(request.headers)

    print("%s %s ->" % (method, request.url))
    url = getServer(request.environ.get("REMOTE_ADDR")) + '/' + p
    print("%s" % (url))

    headers['Host'] = urlparse(url).netloc

    r = requests.request(method=method, url=url, data=body, headers=headers, allow_redirects=False)

    response.status = r.status_code
    for key in r.headers:
        response.headers[key] = r.headers[key]
    return r.content

def getServer(srcIp):
    global currentServer
    global srcIpMap
    if srcIp not in srcIpMap:
        srcIpMap[srcIp] = serverlist[currentServer]
        currentServer = (currentServer + 1) % len(serverlist)
    return srcIpMap[srcIp]

def getServerRoundRobin():
    global currentServer
    res = serverlist[currentServer]
    currentServer = (currentServer + 1) % len(serverlist)
    return res

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    port = config['default']['port']

    global serverlist
    serverlist = config['default']['serverlist'].split(',')

    run(host='0.0.0.0', port=port, server="gunicorn")

if __name__ == "__main__":
    main()