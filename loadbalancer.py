from bottle import route, run, request, response, redirect
import requests
import configparser

server = 'http://localhost' #, 'https://shorturl.brandonchastain.com']
serverports = []
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
    #headers['Host'] = servers[0][8:]
    headers['Host'] = server[7:]
    print("%s %s" % (method, url))
    print("%s" % (body))
    r = requests.request(method=method, url=url, data=body, headers=headers, allow_redirects=False)
    print(r.status_code)
    print(r.headers)
    response.status = r.status_code
    for key in r.headers:
        response.headers[key] = r.headers[key]
    response.body = r.content


def getServer(srcIp):
    global currentServer
    global srcIpMap
    if srcIp not in srcIpMap:
        srcIpMap[srcIp] = serverports[currentServer]
    currentServer = (currentServer + 1) % len(serverports)
    return server + ':' + srcIpMap[srcIp]

def getServerRoundRobin():
    global currentServer
    res = server + ':' + serverports[currentServer]
    currentServer = (currentServer + 1) % len(serverports)
    return res

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    port = config['default']['port']
    global serverports
    serverports = config['default']['serverports'].split(',')
    run(host='0.0.0.0', port=port, server="gunicorn")

if __name__ == "__main__":
    main()