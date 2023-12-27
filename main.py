import json
from io import BytesIO
from logging import getLogger, ERROR
import sys

import httpx
import requests
from bs4 import BeautifulSoup
from flask import Flask, Response, request, send_from_directory

import imdb
import log

app = Flask(__name__)

proxies = {
    "all://": "http://gtdlvpgh-rotate:2j4es4jfjxnr@p.webshare.io:80"
}

httpxClient = httpx.Client(proxies=None, timeout=120)

def genToken(_id):

    h = {}

    headers = """
Host: multiembed.mov
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Connection: keep-alive
Upgrade-Insecure-Requests: 1
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: none
Sec-Fetch-User: ?1
Sec-GPC: 1
TE: trailers
""".strip()

    for l in headers.split("\n"):
        k,v = l.split(":", 1)
        h[k] = v.strip()

    a = requests.get("https://multiembed.mov/?video_id={}".format(_id), headers=h)
    loc = a.headers["location"]
    token = loc.replace("https://streambucket.net/?play=", "")

    return token

def clearOfAds(text):
    soup = BeautifulSoup(text, 'lxml')

    blockedWords = [
        "/ad",
        ".ad",
        "cdn4ads",
        "dontfoid",
        "yiejvik",
        "evwmnd",
        "histats",
        "nfuwpyx",
    ]

    # inject our otterscript.js
    script_tag = soup.new_tag("script")
    script_tag.string = "document.head.appendChild(Object.assign(document.createElement('script'), {src: '/static/js/otterscript.js'}));"

    # Find the head tag and append the script tag
    head_tag = soup.find('head')
    if head_tag is not None:
        head_tag.append(script_tag)

    b = soup.prettify()

    b = b.replace("disableremoteplayback=\"true\"", "") # FUCK YOU LET ME STREAM MY SHI

    return b

    a = soup.find_all(["a", "img", "script"])
    for element in a:
        for blocked in blockedWords:
            if blocked == None: continue
            if element == None: break

            try:
                if blocked in str(element):
                    element.decompose()
                    break
            except TypeError:
                break # for some reason, bs4 does that


    b = soup.prettify()

    b = b.replace("disableremoteplayback=\"true\"", "") # FUCK YOU LET ME STREAM MY SHI

    return b


log.warn("grabbing from bucket..")
bucket = {
    "main.js?v=2": httpxClient.get("https://streambucket.net/js/main.js?v=2").text,
    "main.js?v=3": httpxClient.get("https://streambucket.net/js/main.js?v=3").text,
    "main.css": httpxClient.get("https://streambucket.net/css/main.css?v=16824").text,
    "dd.js": httpxClient.get("https://streambucket.net/js/dd.js").text,
    "playerjs4.js": httpxClient.get("https://streambucket.net/playerjs/playerjs4.js").text,
}

log.info('grabbed from bucket')

@app.route("/")
def index():
    return open("./static/index.html", "r").read()

@app.route('/static/<path:path>')
def serve_file(path):
    return send_from_directory("./static", path, as_attachment=True)

@app.route('/api/imdbSearch', methods=["POST"])
def imdbSearch():
    a = request.get_json(force=True).get("query")

    return Response(json.dumps(imdb.getIMDB(a), indent=4), mimetype="application/json")

@app.route('/api/imdbEps', methods=["POST"])
def imdbEps():
    a = request.get_json(force=True)
    q = a.get("query")

    return Response(json.dumps(imdb.getEps(q, a.get("all", True)), indent=4), mimetype="application/json")

@app.route('/api/imdbInfo', methods=["POST"])
def imdbInfo():
    a = request.get_json(force=True)
    q = a.get("query")

    return Response(json.dumps(imdb.getInfo(q), indent=4), mimetype="application/json")

@app.route('/api/imdbTop', methods=["GET"])
def imdbTop():
    return Response(json.dumps(imdb.getTop(48), indent=4), mimetype="application/json")

@app.route("/api/oscript", methods=["POST"])
def oscript():
    print(request.get_json(force=True))

    return "ok"

# streambucket tunnel

@app.route("/user_guard.php", methods=["POST"])
def uguard():

    h = {}
    ogDomain = "streambucket.net"

    for k,v in request.headers.items():
        h[k] = v.replace("localhost", ogDomain)

    a = requests.post("https://streambucket.net/user_guard.php ", headers=h, data=request.form)

    r = Response(a.text, status=a.status_code)

    return r

@app.route("/vipstream.php")
def proxystream():
    h = {}

    headers = """
Host: streambucket.net
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Connection: keep-alive
Upgrade-Insecure-Requests: 1
Sec-Fetch-Dest: iframe
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: same-origin
Sec-GPC: 1
TE: trailers
    """.strip()

    for l in headers.split("\n"):
        k,v = l.split(":", 1)
        h[k] = v.strip()


    args = ""
    for k,v in request.args.items():
        args += f"&{k}={v}"
    args = args[1:]
    
    baseurl = None
    fancy = True
    if fancy:
        baseurl = "https://streambucket.net/vipstream2.php?"
    else:
        baseurl = "https://streambucket.net/vipstream.php?"
    
    if request.method == "GET":
        a = httpxClient.get("{}{}".format(baseurl, args), headers=h, timeout=60)
    elif request.method == "POST":
        h = {}
        for k,v in request.headers.items():
            h[k] = v.replace("localhost", "streambucket.net")

        url = "{}{}".format(baseurl, args)

        print(h)

        a = requests.post(url, data=request.form, headers=h, timeout=60)

    return Response((a.text), status=a.status_code)


@app.route("/bucket")
def bucketTunnel():
    h = {}
    vid = request.args.get("video_id").strip()
    p = imdb.cache.getFromTokenCache(vid)
    p = False

    if p:
        r = Response("redirect", status=302)
        r.headers["location"] = p.replace("https://streambucket.net/?play=", "/bucket/play?token=")
        return r
    

    headers = """
Host: multiembed.mov
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Connection: keep-alive
Upgrade-Insecure-Requests: 1
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: none
Sec-Fetch-User: ?1
Sec-GPC: 1
TE: trailers
""".strip()
    
    for l in headers.split("\n"):
        k,v = l.split(":", 1)
        h[k] = v.strip()

    a = httpxClient.get("https://multiembed.mov/?video_id={}".format(vid), headers=h)
    loc = a.headers["location"]
    token = loc.replace("https://streambucket.net/?play=", "")

    resp = Response(clearOfAds(a.text), status=a.status_code)
    
    resp.headers["location"] = "/bucket/play?token="+token

    imdb.cache.appendToTokenCache(vid, resp.headers["location"])

    return resp

@app.route("/css/main.css")
def bucketmaincss():
    return Response(bucket["main.css"], mimetype="text/css")

@app.route("/bucket/js/main.js")
def bucketmainjs():
    return Response(bucket["main.js?v="+request.args["v"]], mimetype="text/javascript")

@app.route("/js/main.js")
def bucketmainjs2():
    return Response(bucket["main.js?v="+request.args["v"]], mimetype="text/javascript")

@app.route("/js/dd.js")
def bucketddjs():
    return Response(bucket["dd.js"], mimetype="text/javascript")
    
@app.route("/img/server_icons/<img>")
def ico(img):
    log.debug("image ico request")
    req = httpxClient.get("https://streambucket.net/img/{}".format(img))
    return Response(BytesIO(req.content), status=req.status_code, mimetype="image/jpeg")

@app.route("/playerjs/playerjs4.js")
def bucketplayerjs():
    return Response(bucket["playerjs4.js"], mimetype="text/javascript")

@app.route("/fonts/<fnt>")
def bucketfont(fnt):
    req = httpxClient.get("https://streambucket.net/fonts/{}".format(fnt))
    return Response(BytesIO(req.content), status=req.status_code, mimetype="font/{}".format(fnt.split(".")[-1]))   

@app.route("/captcha/testing/<directory>/<image>")
def captcah(directory, image):
    req = httpxClient.get("https://streambucket.net/captcha/testing/{}/{}".format(directory, image))
    return Response(BytesIO(req.content), status=req.status_code, mimetype="image/jpeg")

@app.route("/playvideo.php", methods=["GET", "POST"])
def playvideo():
    h = {}

    headers = """
Host: streambucket.net
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Connection: keep-alive
Upgrade-Insecure-Requests: 1
Sec-Fetch-Dest: iframe
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: same-origin
Sec-GPC: 1
TE: trailers
""".strip()
    
    for l in headers.split("\n"):
        k,v = l.split(":", 1)
        h[k] = v.strip()

    proxies = None

    if request.method == "GET":
        a = httpx.get("https://streambucket.net/playvideo.php?video_id={}&server_id={}&token={}&init={}".format(request.args["video_id"], request.args["server_id"], request.args["token"], request.args["init"]),
                            headers=h, timeout=60, proxies=proxies)
    elif request.method == "POST":

        args = ""
        for k,v in request.args.items():
            args += f"&{k}={v}"
        args = args[1:]
            
        h = {}
        for k,v in request.headers.items():
            h[k] = v.replace("localhost", "streambucket.net").replace("http://", "https://")

        url = "{}{}".format("https://streambucket.net/playvideo.php?", args)

        print(url)
        print(h)
        a = requests.post(url, data=request.form, headers=h, timeout=60)

    b = a.text

    #b = b.replace("https://streambucket.net/vipstream.php", "/vipstream.php")
    
    return Response((b), status=a.status_code)

@app.route("/response.php", methods=["POST"])
def bucketResponse():

    h = {}

    headers = """
Host: streambucket.net
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0
Accept: */*
Accept-Language: en-US,en;q=0.5
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
X-Requested-With: XMLHttpRequest
Origin: https://streambucket.net
Connection: keep-alive
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
Sec-GPC: 1
TE: trailers
""".strip()
    
    for l in headers.split("\n"):
        k,v = l.split(":", 1)
        h[k] = v.strip()

    a = httpxClient.post("https://streambucket.net/response.php", data=request.form, headers=h, timeout=60)

    b = a.text

    #b = b.replace("https://streambucket.net/vipstream.php", "/vipstream.php")
    
    return Response(clearOfAds(b), status=a.status_code)

@app.route("/bucket/play", methods=["GET", "POST"])
def playBucket():
    token = request.args.get("token")

    h = {}

    headers = """
Host: streambucket.net
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0
Content-Type: application/x-www-form-urlencoded
Accept: text/html;q=0.8
Accept-Language: en-US,en;q=0.5
Connection: keep-alive
Upgrade-Insecure-Requests: 1
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Origin: https://streambucket.net
Sec-Fetch-Site: same-origin
Sec-Fetch-User: ?1
Sec-GPC: 1
TE: trailers
""".strip()
    
    for l in headers.split("\n"):
        k,v = l.split(":", 1)
        h[k] = v.strip()

    if request.method == "GET":
        a = requests.get("https://streambucket.net/?play="+token, headers=h)
    elif request.method == "POST":
        a = requests.post("https://streambucket.net/?play="+token, headers=h, data=request.form)

    b = clearOfAds(a.text).replace("\"/vipstream.php", "https://streambucket.net/vipstream.php")

    resp = Response(b, status=a.status_code)
    #resp.headers["Content-Encoding"] = "br"

    return resp
    

a = getLogger("werkzeug")
#a.setLevel(ERROR)
if "-d" not in ' '.join(sys.argv):
    app.run(host="0.0.0.0", port=443)
else:
    log.debug("debug mode")
    app.run(host="0.0.0.0", port=80)
