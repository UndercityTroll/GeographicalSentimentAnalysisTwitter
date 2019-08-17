from flask import Flask, render_template, request
import folium
import tweepy
import urllib
import json
import math
import textblob

def is_ascii(s):
    accepted = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ,."
    finalValid = True
    for c in s:
        validLetter = False
        for c1 in accepted:
            if c1 == c:
                validLetter=True
        if not validLetter:
            finalValid = False
    if len(s) <= 1:
        finalValid=False
    return finalValid

app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/',methods=['POST'])
def getvalue():
    #everything goes in here

    #code from original thing

    hashtag_phrase = request.form['hashtag_phrase']
    length_string = request.form['length']
    length = int(length_string)


    #code from extracting data


    # variables for analysis
    locationData = {}

    # Step 1 - Authenticate
    consumer_key = 'CONSUMER KEY GOES HERE'
    consumer_secret = 'CONSUMER SECRET GOES HERE'

    access_token = 'ACCESS TOKEN GOES HERE'
    access_token_secret = 'ACCESS TOKEN SECRET GOES HERE'

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    # Specifics for Folium Map API

    m = folium.Map(location=[38.8283, -96.500], zoom_start=5)
    tooltip = "Click for More Info"

    # Step 2 - Specifics of Data

    # Step 3 - Tweet Analysis
    for tweet in tweepy.Cursor(api.search, q=hashtag_phrase + ' -filter:retweets').items(length):
        locat = tweet.author.location
        print(locat, is_ascii(locat))
        if locat is "US" or locat is "USA" or locat is "U.S." or locat is "U.S.A" or locat is "America" or locat is "States":
            locat = "United States"
        if is_ascii(locat):
            # Uses Mapquest API to get information on location
            url = "http://www.mapquestapi.com/geocoding/v1/address?key=MAPQUESTKEYGOESHERE&location=" + locat
            response = urllib.urlopen(url)
            data = json.loads(response.read())
            if not data['info']["messages"]:
                print("no errors")
                # Step 4 - Finds the Lat and Lon from the Mapquest API
                latitude = data["results"][0]["locations"][0]["latLng"]["lat"]
                longitude = data["results"][0]["locations"][0]["latLng"]["lng"]
                if longitude is 98.8508 and latitude is 55.079018:
                    latitude = 55.3781
                    longitude = 1.1743
                # Step 5 - Sentiment Analysis with TextBlob
                analysis = textblob.TextBlob(tweet.text)
                sentiment = analysis.sentiment.polarity
                ExistingLocation = False
                for item in locationData:
                    if item == locat:
                        locationData[item]['count'] += 1
                        locationData[item]['sentiment'] = (
                                    ((locationData[item]['sentiment'] * locationData[item]['count'])
                                     + sentiment) / locationData[item]['count'])
                        ExistingLocation = True
                        print("old tweet")
                if not ExistingLocation:
                    locationData[locat] = {'latitude': latitude, 'longitude': longitude, 'tweet': tweet.text,
                                           'count': 1,
                                           'sentiment': sentiment}
                    print("new tweet")

    # Step 4 - Generate Map
    def rgbtohex(valuer, valueg, valueb):
        converter = "0123456789abcdef"
        hexr = str(converter[(valuer // 16)] + converter[(valuer % 16)])
        hexg = str(converter[(valueg // 16)] + converter[(valueg % 16)])
        hexb = str(converter[(valueb // 16)] + converter[(valueb % 16)])
        return '#' + hexr + hexg + hexb

    for item in locationData:
        sent = int(((locationData[item]['sentiment'] + 1) / 2) * 255)
        sentimentHex = rgbtohex(255 - sent, 0, sent)
        folium.CircleMarker(
            # convert sentiment to hexidecimal gradient
            location=[locationData[item]['latitude'], locationData[item]['longitude']],
            radius=5 * math.sqrt(locationData[item]['count']),
            popup=locationData[item]['tweet'],
            color=sentimentHex,
            fill=False,
            fill_color=sentimentHex
        ).add_to(m)

    m.save('templates/NewMap.html')

    # Printing Done
    print("You have finally reached the end")

    return render_template('NewMap.html')

if __name__ == '__main__':
    app.run(debug=True)
