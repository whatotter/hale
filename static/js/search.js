var stoppedTyping = false
var oldData = ""

document.addEventListener('DOMContentLoaded', function () {

    function checkIfTyping() {
        if (document.getElementById("search").value == oldData) {
            return false
        } else {
            oldData = document.getElementById("search").value
            return true
        }
    }

    var searched = true
    setInterval(function() {
        var typing = checkIfTyping()
            
        if (typing) {
            // if client is still typing
            searched = false
        } else {
            // stopped typing
            console.log('stopped typing')

            if (searched) {
                return
            }

            if (document.getElementById("search").value == "" && oldData == "") {
                searched = true
                showMovies()
                return
            } else if (document.getElementById("search").value == "") {
                return
            }


            var xhr = new XMLHttpRequest()
            xhr.open("POST", "/api/imdbSearch", true)
            xhr.onload = function(){
                var a = JSON.parse(xhr.responseText)
                
                console.log(a)
                
                hideMovies()
                
                for (var i=0; i<Object.keys(a).length; i++) {
                    var itm = a[Object.keys(a)[i]]

                    var skin = {
                        "id": Object.keys(a)[i],
                        "titleType": {
                            "id": itm["type"]
                        },
                        "primaryImage": {
                            "url": itm["imageUrl"]
                        },
                        "runtime": {
                            "seconds": "0"
                        },
                        "titleText": {
                            "text": itm["title"]
                        },

                        "ratingsSummary": {
                            "aggregateRating": "-1",
                            "rank": `Rank: ${itm["rank"]}`
                        },

                        "titleGenres": {
                            "genres": "-1"
                        },

                        "stars": itm["stars"]
                    }
                    
                    createMovieElem(skin)
                    
                }
            }
            console.log(`searching for "${document.getElementById("search").value}"`)
            searched = true
            xhr.send(JSON.stringify({"query": document.getElementById("search").value}))
        }
            
        
    }, 150)
})