import http.client, urllib.request, urllib.parse, urllib.error, base64
headers = {
'Ocp-Apim-Subscription-Key': '292f959e2e7b46eba622d453dea1edac',
}
params = urllib.parse.urlencode({})
conn = http.client.HTTPSConnection('gateway.apiportal.ns.nl')