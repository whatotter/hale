var x = new XMLHttpRequest()
x.open("GET", "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js")
x.onload = function() {
    window.doesAdBlockExist = false
}
x.send(null)
var link = "ad advertisment advertising advert"
// we WANT adblock to block this