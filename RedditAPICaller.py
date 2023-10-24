import sys
import os
from datetime import datetime
import requests
from config.config import ConfigMongo, ConfigReddit
import pymongo

links = ["https://oauth.reddit.com/r/news/top/?t=hour",
        "https://oauth.reddit.com/r/politics/top/?t=hour",
        "https://oauth.reddit.com/r/sports/top/?t=hour",
        "https://oauth.reddit.com/r/worldnews/top/?t=hour",
        "https://oauth.reddit.com/r/technology/top/?t=hour",
        "https://oauth.reddit.com/r/science/top/?t=hour",
        "https://oauth.reddit.com/r/anythinggoesnews/top/?t=hour",
        "https://oauth.reddit.com/r/inthenews/top/?t=hour",
        "https://oauth.reddit.com/r/nottheonion/top/?t=hour",
        "https://oauth.reddit.com/r/offbeat/top/?t=hour",
        "https://oauth.reddit.com/r/onthescene/top/?t=hour",
        "https://oauth.reddit.com/r/qualitynews/top/?t=hour",
        "https://oauth.reddit.com/r/thenews/top/?t=hour",
        "https://oauth.reddit.com/r/upliftingnews/top/?t=hour",
        "https://oauth.reddit.com/r/Full_news/top/?t=hour",
        "https://oauth.reddit.com/r/neutralnews/top/?t=hour",
        "https://oauth.reddit.com/r/environment/top/?t=hour",
        "https://oauth.reddit.com/r/Conservative/top/?t=hour",
        "https://oauth.reddit.com/r/progressive/top/?t=hour",
        "https://oauth.reddit.com/r/Libertarian/top/?t=hour",
        "https://oauth.reddit.com/r/Futurology/top/?t=hour",
        "https://oauth.reddit.com/r/LateStageCapitalism/top/?t=hour",
        "https://oauth.reddit.com/r/movies/top/?t=hour",
        "https://oauth.reddit.com/r/TrueFilm/top/?t=hour",
        "https://oauth.reddit.com/r/Music/top/?t=hour",
        "https://oauth.reddit.com/r/entertainment/top/?t=hour",
        "https://oauth.reddit.com/r/MovieSuggestions/top/?t=hour",
        ]

#Create a mongoDB connection
def createServerConnection():
    client = pymongo.MongoClient(ConfigMongo.host, ConfigMongo.port)
    db = client[ConfigMongo.database]
    collection = db[ConfigMongo.collection]

    return client, collection

#Close the mongoDB connection
def closeServerConnection(client):
    client.close()

#Function to convert responses to format to insert into the DB
def insertResponses(res, client, collection):
    #print(res.json()['data']['dist'])
    subreddit = res.json()['data']['children']
    for subR in subreddit:
        #print(subR['data']['title'], " ", datetime.fromtimestamp(subR['data']['created_utc']))
        collection.insert_one(subR['data'])

#Authenticate API by providing token and other details
def authAPI():
    auth = requests.auth.HTTPBasicAuth(
        "iYAaR2qDuJgnoBMg45lMIA", "LL5rD1_Iq4tpbnaoRs-JdhUA1imbMA"
    )
    data = {
        "grant_type": "password",
        "username": ConfigReddit.username,
        "password": ConfigReddit.password,
    }
    headers = {"User-Agent" : "MyAPI/0.0.1"}
    res = requests.post(
        "https://www.reddit.com/api/v1/access_token",
        auth=auth,
        data=data,
        headers=headers,
    )

    accessToken = res.json()['access_token']
    headers['Authorization'] = f'bearer {accessToken}'

    return headers

#Call the apis one by one
def callRedditAPI(headers, client, collection):
    try:
        params = {"limit" : 100}
        for link in links:
            res = requests.get(link, headers=headers,
                params=params)
            insertResponses(res, client, collection)
    except ValueError:
        print("One of the reddit is not alive")

def main():
    headers = authAPI()
    client, collection = createServerConnection()
    try:
        callRedditAPI(headers, client, collection)
    except ValueError:
        print("Error connecting with database")
    closeServerConnection(client)

if __name__ == "__main__":
    main()
