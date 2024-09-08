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
    

a = getLogger("werkzeug")
#a.setLevel(ERROR)
if "-d" not in ' '.join(sys.argv):
    app.run(host="0.0.0.0", port=443)
else:
    log.debug("debug mode")
    app.run(host="0.0.0.0", port=80)
