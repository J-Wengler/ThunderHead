from thunderhead import ThunderHead
import http.client, urllib

thunder = ThunderHead("Mandajacobson98", "Cayman2ajw!!", change = -30, low = 60, high = 275)
try:
    thunder.watch()
except Exception as e:
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
    urllib.parse.urlencode({
        "token": "a7hxahk94ajn8tyt5y13wnq4dwia1t",
        "user": "u39yretpf7kpu775jm8djwey42t8jh",
        "title": "ThunderHead Issue",
        "message": f"{e}",
    }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()
