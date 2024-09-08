import requests
import json
import datetime
import base64
from bs4 import BeautifulSoup
import time
import threading
import log


cachedIds     =  json.loads(open("./cache/cached.json", "r").read())
cachedSzns    =  json.loads(open("./cache/szns.json", "r").read())
cachedEps     =  json.loads(open("./cache/eps.json", "r").read())
cachedMovies  =  json.loads(open("./cache/movs.json", "r").read())
cachedTokens  =  json.loads(open("./cache/tokens.json", "r").read())

def getDate():
    return str(datetime.datetime.now().strftime("%Y-%m-%d"))

class cache:
    die = False
    def checkIfCached(_id):
        return _id in cachedIds
            
    def appendToSznCache(_id, z):
        if not cache.checkIfCached(_id):
            cachedSzns[_id] = z
            cachedIds[_id] = None

        return True
    def appendToEpsCache(_id, z):
        if not cache.checkIfCached(_id):
            cachedEps[_id] = z
            cachedIds[_id] = None

        return True
    def appendToMovCache(_id, z):
        if not cache.checkIfCached(_id):
            cachedMovies[_id] = z
            cachedIds[_id] = None

        return True
    

    def getFromCache(_id, file):
        if cache.checkIfCached(_id):
            if file == "movs":
                data = cachedMovies
            elif file == "eps": 
                data = cachedEps
            elif file == "szns":
                data = cachedSzns

            return data[_id]
        else:
            return False
        
    def appendToTokenCache(_id, token):
        log.info("token \"{}\" was cached for id \"{}\"".format(token, _id))
        if _id not in list(cachedTokens):
            cachedTokens[_id] = token
        return True
    
    def getFromTokenCache(_id):
        if _id in list(cachedTokens):
            return cachedTokens[_id]
        return False

    def cacheDumper():
        """
        thread
        """

        log.info("started caching daemon")

        while True:
            if cache.die:
                return
            else:
                time.sleep(30)
                
                cacheTable = {
                    "./cache/cached.json": cachedIds,
                    "./cache/szns.json": cachedSzns,
                    "./cache/eps.json": cachedEps,
                    "./cache/movs.json": cachedMovies,
                    "./cache/tokens.json": cachedTokens
                }

                for k,v in cacheTable.items():
                    with open(k, "w") as f:
                        f.write(json.dumps(v, indent=4))
                        f.flush()


def getIMDB(title):
    a = title.replace(" ", "%20")
    a = requests.get("https://v3.sg.media-imdb.com/suggestion/x/{}.json?includeVideos=1".format(a))

    movies = {}

    if a.status_code == 200:
        
        b = json.loads(a.text)["d"]


        for x in b:
            rType = x.get("qid")
            if rType == "movie" or rType == "tvSeries":
                try:
                    imageUrl = x["i"]["imageUrl"]
                except:
                    imageUrl = None

                movies[x["id"]] = {
                    "imageUrl": imageUrl,
                    "title": x["l"],
                    "stars": x["s"],
                    "rank": x["rank"],
                    "type": rType
                }

        return movies
    else:
        log.error(a.status_code)
        log.error(a.text)
    
def getTop(limit):
       
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.5",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Host": "www.imdb.com",
        "Pragma": "no-cache",
        "Referer": "https://www.imdb.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0"
    }
       
    a = requests.get("https://www.imdb.com/chart/top/", headers=headers)
    soup = BeautifulSoup(a.text, "lxml")

    b = json.loads(soup.findAll("script", {"type": "application/json", "id": "__NEXT_DATA__"})[0].string)["props"]["pageProps"]["pageData"]["chartTitles"]

    movies = {}

    p = 0
    if a.status_code == 200:
        try:
            g = b["edges"]

            for i in g:

                if p == limit:
                    break

                node = i["node"]

                movies[node["id"]] = node
                p += 1

            return movies
        except:
            raise

    else:
        log.error(a.status_code)
        log.error(a.text)
        raise KeyError("incorrect data passed")


    return movies

def grabMovInfo(_id):
    urlID = base64.b64encode("https://www.imdb.com/title/{}/".format(_id).encode('ascii')).decode('ascii')

    if not cache.checkIfCached(urlID):

        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Host": "www.imdb.com",
            "Pragma": "no-cache",
            "Referer": "https://www.imdb.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0"
        }

        a = requests.get("https://www.imdb.com/title/{}/".format(_id), headers=headers).text

        soup = BeautifulSoup(a, "lxml")

        a = json.loads(soup.findAll("script", {"type": "application/ld+json"})[0].string)

        a.pop('review')
        a.pop('trailer')

        cache.appendToMovCache(urlID, a)

        log.info("{} was not found in cache, so a request was made for it to be put into the cache (grabMovInfo())".format(_id))

    else:
        a = cache.getFromCache(urlID, "movs")
        log.debug("{} was found in cache".format(_id))

    return a

def grabEPInfo(_id, season):
    urlID = base64.b64encode('https://www.imdb.com/_next/data/AznRvB1QnY0m1h3Jklqtf/title/{}/episodes.json?season={}&tconst={}'.format(_id, season, _id).encode('ascii')).decode('ascii')

    if not cache.checkIfCached(urlID):

        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Host": "www.imdb.com",
            "Pragma": "no-cache",
            "Referer": "https://www.imdb.com/title/{}/episodes/".format(_id),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0"
        }

        a = requests.get('https://www.imdb.com/_next/data/AznRvB1QnY0m1h3Jklqtf/title/{}/episodes.json?season={}&tconst={}'.format(_id, season, _id), headers=headers)
        
        print(a.text)
        b = json.loads(a.text)

        if a.status_code == 200:
            log.info("{} was not found in cache, so a request was made for it to be put into the cache (grabEPInfo())".format(_id))
            cache.appendToSznCache(urlID, b)

        else:
            log.error("didn't save to cache: {}".format(a.status_code))
            raise KeyError("id is likely not for a series")
        
    else:
        log.debug("{} was found in cache".format(_id))
        b = cache.getFromCache(urlID, "szns")

    return b


def getEps(_id, allSzns=True):
    # explaining this:
    # get the INITIAL season (s1), and the the request returns how many seasons there is
    # so, if you fetch one, you get all

    a = grabEPInfo(_id, 1)

    seasons = 1

    eps = {}

    b = a["pageProps"]["contentData"]

    seasons = len(b["section"]["seasons"])

    eps["s1"] = []
    for x in b["section"]["episodes"]["items"]:
        eps["s1"].append(x)

    if seasons != 1 and allSzns:
        for season in range(1, seasons): # start at season 2 since we got season 1
            season = season+1
            b = grabEPInfo(_id, season)["pageProps"]["contentData"]

            eps["s{}".format(season)] = []
            for x in b["section"]["episodes"]["items"]:
                eps["s{}".format(season)].append(x)

    return eps 

    
def getInfo(_id):
    a = None
    return grabMovInfo(_id)

    if _id in list(cachedIds): # if it's cached
        # do this to prevent the amount of requests sent (2 -> 1)
        if not cachedIds[_id]["isMovie"]: # if its a series
            a = grabEPInfo(_id, 1) # return from cache
        else: # is movie
            a = grabMovInfo(_id)

        print('| AUTODETERMINED FROM CACHE')
    else:
        # find out if it's a movie or a series
        cachedIds[_id] = {}
        try:
            cachedIds[_id]["isMovie"] = False # is a series
            a = grabEPInfo(_id, 1)
        except:
            cachedIds[_id]["isMovie"] = True # is a movie
            a = grabMovInfo(_id)

        print('| REQUEST MADE')

    print("")
    return a

threading.Thread(target=cache.cacheDumper, daemon=True).start()