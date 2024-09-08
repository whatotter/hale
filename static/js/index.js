var sznsLoaded = []
var starsLoaded = []
var rwLoaded = []
var starElem = document.getElementById("starred")
let storage = window.localStorage;
var firstInit = false
var finished = false


console.log(storage.getItem("viewed"))
if (storage.getItem("viewed") == undefined || storage.getItem("viewed") == "") {
    storage.setItem("viewed", JSON.stringify([]));
}

console.log(storage.getItem("epsViewed"))
if (storage.getItem("epsViewed") == undefined || storage.getItem("epsViewed") == "") {
    storage.setItem("epsViewed", JSON.stringify([]));
}

console.log(storage.getItem("fancyplayer"))
if (storage.getItem("fancyplayer") == undefined || storage.getItem("fancyplayer") == "") {
    storage.setItem("fancyplayer", false);
}

console.info(storage.getItem("starred"))
if (storage.getItem("starred") == undefined || storage.getItem("starred") == "") {
    storage.setItem("starred", JSON.stringify([]));
}

console.info(storage.getItem("mostRecent"))
if (storage.getItem("mostRecent") == undefined || storage.getItem("mostRecent") == "") {
    storage.setItem("mostRecent", undefined);
}


function secondsToHms(d) {
    d = Number(d);
    var h = Math.floor(d / 3600);
    var m = Math.floor(d % 3600 / 60);
    var s = Math.floor(d % 3600 % 60);

    var hDisplay = h > 0 ? h + (h == 1 ? " hour, " : " hours, ") : "";
    var mDisplay = m > 0 ? m + (m == 1 ? " minute, " : " minutes, ") : "";
    var sDisplay = s > 0 ? s + (s == 1 ? " second" : " seconds") : "";

    var stri = (hDisplay + mDisplay + sDisplay)

    return stri.slice(0, -2); 
}

function createMovieElem(data, ovrRecent, ovrStarred, prepend) {
    var fullContainerDiv = document.createElement('div')
    var containerDiv = document.createElement('a');
    
    var dataDiv = document.createElement('div');

    var imageElement = document.createElement('img');
    var heading2Element = document.createElement('h2');
    var star = document.createElement("i")
    star.tabIndex = 0

    var isStarred = false
    var recentlyWatched = false

    var id = data["id"]

    
    var st = JSON.parse(storage.getItem("starred"));
    
    var rw = JSON.parse(storage.getItem("viewed"));
    
    if (st.includes(data["id"])) {
        star.className = "fa-solid fa-star star"
        console.warn(`${id} ${data["titleText"]["text"]} IS IN ${st}`)
        isStarred = true
    } else {
        star.className = "fa-regular fa-star star"
        isStarred = false
    }
    
    if (rw.includes(data["id"])) {
        console.log('recently watched')
        recentlyWatched = true
    }
    

    star.addEventListener('keydown', function(event) {
        console.warn(event.code)
        if (event.code === 32) {
          event.preventDefault();
          this.click();
        }
      });

    star.addEventListener("click", function() { // listener for the favorite star
        
        var st = JSON.parse(storage.getItem("starred"));
        
        if (!isStarred) { // if it isn't starred
            // star it
            star.className = "fa-solid fa-star star"
            st.push(data["id"])
            
            fullContainerDiv.remove()
            
        } else {
            star.className = "fa-regular fa-star star"
            if (st.includes(data["id"])) {
                var idex = st.indexOf(data["id"])
                var idex2 = starsLoaded.indexOf(data["id"])
                
                st.splice(idex, 1)
                starsLoaded.splice(idex2, 1)
                
                fullContainerDiv.remove()
            }
        }
        
        isStarred = !isStarred
        
        storage.setItem("starred", JSON.stringify(st))
        createMovieElem(data, undefined, undefined, true)
    })
    
    
    var isMovie = true
    
    var subheadings = [];
    
    for (var i = 0; i < 3; i++) {
        subheadings[i] = document.createElement('h4');
        subheadings[i].className = "movie-extra"
    }
    
    
    fullContainerDiv.className = "movie"
    
    dataDiv.className = "movie-data"
    
    
    // season-ep dropdown
    
    var seasonDropdown = document.createElement("select")
    seasonDropdown.className = "sdrop"
    
    var seOpt = document.createElement('option')
    seOpt.innerHTML = "S1 E1"
    seOpt.value = "s1_e1"
    seasonDropdown.appendChild(seOpt)
    
    seasonDropdown.addEventListener("change", function() {
        console.log(this.value)
        
        var a = this.value.split("_")
        var s = a[0].replace("s", "")
        var e = a[1].replace("e", "")
        
        if (storage.getItem("fancyplayer")) {
            prependURL = "https://multiembed.mov/directstream.php?video_id="
        } else {
            prependURL = "/bucket?video_id="
        }
        containerDiv.href = prependURL+data["id"]+`&s=${s}&e=${e}`
    })
    
    seasonDropdown.addEventListener("click", function() {
        console.warn(`loading szns for ${data["id"]}`)
        if (sznsLoaded.includes(data["id"])) {
            return
        }
        
        seOpt.innerHTML = "loading seasons and episodes.."
        
        xhr = new XMLHttpRequest()
        xhr.open("POST", "/api/imdbEps", true)
        xhr.onload = function() {
            seasonDropdown.removeChild(seOpt)
            var a = JSON.parse(xhr.responseText)
            sznsLoaded.push(data["id"])

            var svw = JSON.parse(storage.getItem("epsViewed"))
            
            for (var i=0; i<Object.keys(a).length; i++) {
                var itm = Object.keys(a)[i]
                
                for (var b=0; b<a[itm].length; b++) {
                    var newOpt = document.createElement('option')
                    
                    // !!!! SZN CHECK !!!!
                    
                    var szn = a[itm][b]["season"]
                    var ep = a[itm][b]["episode"]
                    var titl = a[itm][b]["titleText"]
                    var val = data["id"]+"_"+`s${szn}_e${ep}`

                    console.warn(svw)
                    console.warn(val)
                    if (svw.includes(val)) {
                        console.log("did the thingy")
                        titl += " | ✅" // the most buttfuck ass fix for this but it works
                    }
                    
                    newOpt.innerHTML = `S${szn} E${ep} | ${titl}`
                    newOpt.value = `s${szn}_e${ep}`
                    
                    seasonDropdown.appendChild(newOpt)
                    
                }
            }
        }
        xhr.send(JSON.stringify({"query": data["id"]}))
    })
    
    
    if (data["titleType"]["id"] == "movie") {
        if (data["runtime"]["seconds"] != "0") {
            subheadings[0].textContent = `movie length: ${secondsToHms(parseInt(data["runtime"]["seconds"]))}`;
        } else {
            subheadings[0].textContent = "Movie"
        }
    } else {
        subheadings[0].textContent = `TV series`;
        isMovie = false
    }
    
    containerDiv.target = "_blank"
    containerDiv.addEventListener("click", function() {

        if (isMovie) {
            var vw = JSON.parse(storage.getItem("viewed"));
    
            if (!vw.includes(data["id"])) {
                vw.push(data["id"])
                storage.setItem("viewed", JSON.stringify(vw))
            }
        } else {
            var svw = JSON.parse(storage.getItem("epsViewed"))
            var val = data["id"]+"_"+seasonDropdown.value

            if (!svw.includes(val)) {
                svw.push(val)
                storage.setItem("epsViewed", JSON.stringify(svw))
            }
        }

        storage.setItem("mostRecent", data["id"]);
    })

    if (storage.getItem("fancyplayer") == "true") {
        prependURL = "https://multiembed.mov/directstream.php?video_id="
    } else {
        prependURL = "https://multiembed.mov/?video_id="
    }
    
    if (isMovie) {
        containerDiv.href = prependURL+data["id"]
    } else {
        containerDiv.href = prependURL+data["id"]+`&s=1&e=1`
    }
    
    // Set content and attributes
    imageElement.src = data["primaryImage"]["url"];
    
    
    
    if (30 >= data["titleText"]["text"].length) {
        heading2Element.textContent = data["titleText"]["text"];
    } else {
        data["titleText"]["text"] = data["titleText"]["text"].slice(0, 30-data["titleText"]["text"].length) + "..."
        heading2Element.textContent = data["titleText"]["text"];
    }
    heading2Element.className = "movie-title"

    if (data["ratingsSummary"]["aggregateRating"] != "-1") {
        subheadings[1].textContent = data["ratingsSummary"]["aggregateRating"] + "/10 (" + data["ratingsSummary"]["voteCount"] + " votes)";
    } else {
        subheadings[1].textContent = data["ratingsSummary"]["rank"]
    }
    
    if (data["titleGenres"]["genres"] != '-1') {
        var genres = []
        var genresData = data["titleGenres"]["genres"]
        for (var i=0; i<genresData.length; i++) {
            genres.push(genresData[i]["genre"]["text"])
        }
    
        subheadings[2].textContent = genres.join(', ');
    } else {
        subheadings[2].textContent = data['stars']
    }

    // Append elements to containerDiv
    containerDiv.appendChild(imageElement);

    dataDiv.appendChild(heading2Element);
    
    for (var i = 0; i < 3; i++) {
        dataDiv.appendChild(subheadings[i]);
    }
    
    
    
    // Append containerDiv to the body or any other desired parent element
    
    fullContainerDiv.appendChild(containerDiv)
    fullContainerDiv.appendChild(star)
    fullContainerDiv.appendChild(dataDiv)

    if (!isMovie) { 
        fullContainerDiv.appendChild(seasonDropdown)
    }

    if (ovrRecent != undefined) {
        recentlyWatched = ovrRecent
    }

    if (ovrStarred != undefined) {
        isStarred = ovrStarred
    }

    if (!isStarred && !recentlyWatched) {
        if (prepend) {
            document.getElementById("movies").prepend(fullContainerDiv)
        } else {
            document.getElementById("movies").appendChild(fullContainerDiv);
        }
    } else {
        console.log("----------")
        console.log(isStarred)
        console.log(ovrStarred)

        if (isStarred) {
            console.log("isStarred")

            if (starsLoaded.includes(data["id"])) {
                return
            }

            if (ovrStarred) {
                starsLoaded.push(data["id"])
                document.getElementById("starred").appendChild(fullContainerDiv);
                return
            }
            createMovieElem(data, false, true, false)
        }
    
        if (recentlyWatched) {
            console.log("recent")

            if (rwLoaded.includes(data["id"])) {
                return
            }

            if (ovrRecent) {
                rwLoaded.push(data["id"])
                document.getElementById("recent").appendChild(fullContainerDiv);
                return
            }
            createMovieElem(data, true, false, false)
        }
    }
    
}

function destroyMovies() {
    while (document.getElementById("movies").firstChild) {
        document.getElementById("movies").removeChild(document.getElementById("movies").firstChild);
    }

    while (document.getElementById("starred").firstChild) {
        document.getElementById("starred").removeChild(document.getElementById("starred").firstChild);
    }

    while (document.getElementById("recent").firstChild) {
        document.getElementById("recent").removeChild(document.getElementById("recent").firstChild);
    }

    starsLoaded = []
}

function showStarred() {
    var b = document.getElementById("starred").children
    for (i=0; i<b.length; i++) {
        var elem = b[i]
        elem.style.display = 'block'
    }
}

function showRecent() {
    var b = document.getElementById("recent").children
    for (i=0; i<b.length; i++) {
        var elem = b[i]
        elem.style.display = 'block'
    }
}

function showMovies() {

    var b = document.getElementById("movies").children
    for (i=0; i<b.length; i++) {
        var elem = b[i]
        elem.style.display = 'block'
    }

    var b = document.getElementById("starred").children
    for (i=0; i<b.length; i++) {
        var elem = b[i]
        elem.style.display = 'block'
    }

    var b = document.getElementById("recent").children
    for (i=0; i<b.length; i++) {
        var elem = b[i]
        elem.style.display = 'block'
    }

    starsLoaded = []
}

function hideStarred() {
    var b = document.getElementById("starred").children
    for (i=0; i<b.length; i++) {
        var elem = b[i]
        elem.style.display = 'none'
    }
}

function hideRecent() {
    var b = document.getElementById("recent").children
    for (i=0; i<b.length; i++) {
        var elem = b[i]
        elem.style.display = 'none'
    }
}

function hideMovies() {

    var b = document.getElementById("movies").children
    for (i=0; i<b.length; i++) {
        var elem = b[i]
        elem.style.display = 'none'
    }

    var b = document.getElementById("starred").children
    for (i=0; i<b.length; i++) {
        var elem = b[i]
        elem.style.display = 'none'
    }

    var b = document.getElementById("recent").children
    for (i=0; i<b.length; i++) {
        var elem = b[i]
        elem.style.display = 'none'
    }

    starsLoaded = []
}

function loadFromId(id) {
    const penis = new XMLHttpRequest()
    penis.open("POST", "/api/imdbInfo", true)
    penis.onload = function() {
        var a = JSON.parse(penis.responseText)
        var skin = {}

        if (!Object.keys(a).includes("@context")) {
            var skin = {
                "id": id,
                "titleType": {
                    "id": a['pageProps']["contentData"]["posterData"]["type"]
                },
                "primaryImage": {
                    "url": a['pageProps']["contentData"]["posterData"]["image"]["url"]
                },
                "runtime": {
                    "seconds": "0"
                },
                "titleText": {
                    "text": a['pageProps']["contentData"]["entityMetadata"]["titleText"]["text"]
                },

                "ratingsSummary": {
                    "aggregateRating": "-1",
                    "rank": `${a["pageProps"]["contentData"]["entityMetadata"]["ratingsSummary"]["aggregateRating"]}/10`
                },

                "titleGenres": {
                    "genres": a["pageProps"]["contentData"]["entityMetadata"]["titleGenres"]["genres"]
                },
            }
            
        } else {

            var result = a.hasOwnProperty('duration') ? a.duration : 'PT0H0M'

            var d = result.replace("PT", "").replace("H", ":").replace("M", ":") + "0"
            var timeEpoch = d.split(':'); // split it at the colons

            // minutes are worth 60 seconds. Hours are worth 60 minutes.
            var seconds = (+timeEpoch[0]) * 60 * 60 + (+timeEpoch[1]) * 60 + (+timeEpoch[2]); 

            var skin = {
                "id": id,
                "titleType": {
                    "id": a["@type"].toLowerCase()
                },
                "primaryImage": {
                    "url": a["image"]
                },
                "runtime": {
                    "seconds": seconds
                },
                "titleText": {
                    "text": a["name"]
                },

                "ratingsSummary": {
                    "aggregateRating": a["aggregateRating"]["ratingValue"],
                    "voteCount": a["aggregateRating"]["ratingValue"]
                },

                "titleGenres": {
                    "genres": []
                },
            }

            for (var i=0; i<a["genre"].length; i++) {
                skin["titleGenres"]["genres"].push({"genre": {"text": a["genre"][i]}})
            }
        }

        createMovieElem(skin, undefined, undefined, false)
        hideStarred()
        hideRecent()
    

    }
    penis.send(JSON.stringify({"query": id}))
}

function renewFront() {
    destroyMovies()
    
    if (document.getElementById("search").value != "") {
        return
    }
    
    console.warn('got TOP MOVIES')

    var movies = [];
    var sel = ""
    var xhr = new XMLHttpRequest()
    xhr.open("GET", "/api/imdbTop", true)
    xhr.onload = function(){
        
        
        movies = JSON.parse(xhr.responseText)
        
        for (var i=0; i<Object.keys(movies).length; i++) {
            var itm = Object.keys(movies)[i]
            createMovieElem(movies[itm], undefined, undefined, false)
        }

        console.info("done loading movies")
        console.info("loaded these stars:")
        console.info(starsLoaded)

        if (storage.getItem("starred") == undefined || storage.getItem("starred") == "") {
            storage.setItem("starred", JSON.stringify([]));
        } else {
            var stars = JSON.parse(storage.getItem("starred")).concat(JSON.parse(storage.getItem("viewed")))
            
            for (var i=0; i<stars.length; i++) {
                sel = stars[i]

                console.error("STAR " + sel)
                console.error(starsLoaded)
    
                if (!starsLoaded.includes(stars[i])) {
                    loadFromId(sel)
                }
            }
        }
    }
    xhr.send()
}

document.addEventListener('DOMContentLoaded', function () {
    var a = false
    var isChecked = false

    document.getElementById("starred-chevron").addEventListener("click", function() {
        if (document.getElementById("starred").children[0].style.display == "none") {
            showStarred()
            document.getElementById("starred-chevron").style.transform = "rotate(180deg)"
        } else {
            hideStarred()
            document.getElementById("starred-chevron").style.transform = "rotate(0deg)"
        }
    })

    document.getElementById("recent-chevron").addEventListener("click", function() {
        if (document.getElementById("recent").children[0].style.display == "none") {
            showRecent()
            document.getElementById("recent-chevron").style.transform = "rotate(180deg)"
        } else {
            hideRecent()
            document.getElementById("recent-chevron").style.transform = "rotate(0deg)"
            
        }
    })



    if (storage.getItem("fancyplayer") == "false") {
        isChecked = false
    } else {
        isChecked = true
    }

    document.getElementById("vip").checked = isChecked
    document.getElementById("vip").addEventListener("change", function() {
        storage.setItem("fancyplayer", this.checked)
        isChecked = this.checked
        window.location = "/"
    })

    storage.setItem("init", false)
    renewFront()
    storage.setItem("init", true)


    particlesJS.load('particles-js', 'static/particles.json', function() {
        console.log('callback - particles.js config loaded');
      });

    
    if (window.doesAdBlockExist == undefined) {
        console.log("adblock exists!")
        document.getElementById("hasadblock").innerHTML = "did detect an adblocker, that's <span style=\"color: green; font-weight: bold\">good!</span>"
    } else {
        console.log("adblock does not exist :(")
        document.getElementById("hasadblock").innerHTML = "did not detect an adblocker, that's <span style=\"color: red; font-weight: bold\">bad.</span> go install one"
    }
})
