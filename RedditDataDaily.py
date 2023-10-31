import sys
import os
from datetime import datetime
import requests
from config.config import ConfigMongo, ConfigReddit
import pymongo

links = ["https://oauth.reddit.com/r/politics/top/?t=hour"
        ]

#Create a mongoDB connection
def createServerConnection():
    client = pymongo.MongoClient(ConfigMongo.host, ConfigMongo.port)
    db = client[ConfigMongo.database]
    collection = db[ConfigMongo.collectionRedditDates]
    collectionComments = db[ConfigMongo.collectionCommentsHour]

    return client, collection, collectionComments

#Close the mongoDB connection
def closeServerConnection(client):
    client.close()

#Function to convert responses to format to insert into the DB
def insertResponses(res, client, collection, collectionComments,headers):
    #print(res.json()['data']['dist'])
    subreddit = res.json()['data']['children']
    for subR in subreddit:
        #print(subR['data']['title'], " ", datetime.fromtimestamp(subR['data']['created_utc']))
        subR['data']["dateTime"] = str(datetime.now())
        collection.insert_one(subR['data'])

        #Get the comments with that article
        id = subR['data']['permalink']
        params = {"limit" : 100}
        print("https://oauth.reddit.com" + id)
        childs = requests.get("https://oauth.reddit.com" + id, headers=headers,
                params=params)
        childComments = childs.json()[1]['data']['children']
        for every in childComments:
            every['data']['datetime'] = str(datetime.now())
            collectionComments.insert_one(every['data'])


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
def callRedditAPI(headers, client, collection, collectionComments):
    try:
        params = {"limit" : 100}
        for link in links:
            res = requests.get(link, headers=headers,
                params=params)
            insertResponses(res, client, collection, collectionComments, headers)
    except ValueError:
        print("One of the reddit is not alive")

def main():
    headers = authAPI()
    client, collection, collectionComments = createServerConnection()
    try:
        callRedditAPI(headers, client, collection, collectionComments)
    except ValueError:
        print("Error connecting with database")
    closeServerConnection(client)

if __name__ == "__main__":
    main()
