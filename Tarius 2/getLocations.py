import googlemaps
import os
import json
import requests
import time

def getLocationsMain(location):
    defaultLocation = "Santa Clara"
    if not location:
      location = defaultLocation
    
    # return:
    namelist = []
    photolist = []
    placeidlist = []

    # other:
    apikey = os.environ['apikeysecret']
    gmaps = googlemaps.Client(key=apikey)
    hourslist = []
    ratinglist = []
    userratinglist = []
    typeslist = []
    vicinitylist = []
    reviewlist = []
    totaldifference = 0

    '''def matchLocations(name, place_id, totaldifference):
        payload = {}
        headers = {}
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json?query=" + name + "&key=" + apikey
        jdata = json.loads(requests.request("GET", url, headers=headers, data=payload).text)
        print(jdata["results"])
        if jdata["results"][0].get("name") == name and jdata["results"][0].get("place_id") != place_id:
            totaldifference += 1 
            return False

        else:
            return True'''

    def getLocations(url):
        print("blahhahahahha")
        payload = {}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        jdata = json.loads(response.text)
        countervar = 0

        while countervar <= len(list(jdata["results"])) - 1:        
            
            name = list(jdata["results"])[countervar].get("name")
            types = list(jdata["results"])[countervar].get("types")
            placeidlist.append(list(jdata["results"])[countervar].get("place_id")) 

            include = True
            if include == True:
                namelist.append(name)
                hourslist.append(list(jdata["results"])[countervar].get("opening_hours"))
                photolist.append(list(jdata["results"])[countervar].get("photos"))
                ratinglist.append(list(jdata["results"])[countervar].get("rating"))
                userratinglist.append(list(jdata["results"])[countervar].get("user_ratings_total"))
                typeslist.append(types)
                vicinitylist.append(list(jdata["results"])[countervar].get("vicinity"))
                url = "https://maps.googleapis.com/maps/api/place/details/json?place_id=" + list(jdata["results"])[countervar].get("place_id") + "&fields=name,rating,formatted_phone_number,reviews&key=" + apikey
                payload={}
                headers = {}
                '''if len(json.loads(requests.request("GET", url, headers=headers, data=payload).text)["result"]) == 4:
                    reviews = list(json.loads(requests.request("GET", url, headers=headers, data=payload).text)['result'].get("reviews"))
                    reviewlist.append(reviews[0].get("text") + reviews[1].get("text") + reviews[2].get("text"))'''
            else:
                print("removed", name)

            countervar += 1

    location = gmaps.geocode(location)[0] #like -33.8670522%2C151.1957362
    coords = str(location.get("geometry").get("bounds").get(("northeast")).get("lat")) + "%2C" + str(location.get("geometry").get("bounds").get(("northeast")).get("lng"))

    radius = "16093"
    type = 'charity'
    keyword = 'volunteer'

    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=" + coords + "&radius=" + radius + "&type=" + type + "&keyword=" + keyword + "&key=" + apikey
    getLocations(url)

    headers = {}
    payload ={}
    response = requests.request("GET", url, headers=headers, data=payload)
    jdata = json.loads(response.text)

    if len(list(jdata["results"])) == 20 - totaldifference:
        print("second go:")
        url2 = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=" + coords + "&radius=" + radius + "&type=" + type + "&keyword=" + keyword + "&key=" + apikey + "&pagetoken=" + jdata.get("next_page_token")
        time.sleep(2)
        getLocations(url2)

    print("nknkn", len(namelist))
    print(namelist)

    returnFinal = []
    returnFinal.append(namelist)
    returnFinal.append(photolist)
    returnFinal.append(placeidlist)

    return returnFinal