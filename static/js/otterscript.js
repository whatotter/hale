/*
hello mr whoever is viewing this script

this is not a script that harnesses ads, spawns ads, etc.
this is only to submit the m3u8 playlist to the central server, so it could be downloaded and streamed from there instead
aka make low quality video higher quality, but next time

its completely non-invasive, and exits after the m3u8 player has spawned
if you want, you can block this script, but i politely ask you dont

thanks,
    - otter (otterwrks.co)
*/

var found = false
let storage = window.localStorage;

function findM3U8PL(){
    a = document.getElementsByTagName("video")

    console.warn(a)

    for (var i=0; i<a.length; i++) {
        if (a[i].src.includes(".m3u8")) {
            console.log("[otterscript] found m3u8")

            alert(a[i].src)

            var id = storage.getItem("mostRecent")

            var xhr = new XMLHttpRequest()
            xhr.open("POST", "http://localhost/api/oscript")
            xhr.send(JSON.stringify({"pl": a[i].src, "id": id}))

            found = true
            break
        }
    }

    if (!found) {
        console.warn("[oscript] not found")
        setTimeout(findM3U8PL, 1000)
    }
}

document.addEventListener("DOMContentLoaded", function() {
    if (document.location.origin == "https://streambucket.net") {
        findM3U8PL()
    } else {
        console.log(document.location.origin)
    }
})