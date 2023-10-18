import logging
import sys
import time
import warnings
from datetime import datetime

import requests
from config.config import creds_reddit, creds_mongodb
import http.client
import pymongo
import json

# This sets the root logger to write to stdout (your console).
logging.basicConfig()
warnings.filterwarnings("ignore")

# Create the MongoDB connection
def create_server_connection():
    client = pymongo.MongoClient(creds_mongodb.host, creds_mongodb.port)
    db = client[creds_mongodb.database]
    collection = db[creds_mongodb.collection]

    return client, collection

# Close the MongoDB connection
def close_server_connection(client):
    client.close()


# we use this function to convert responses to dataframes
def insert_response(res, client, collection):
    print(res.json()['data']['dist'])

    subreddit = res.json()['data']['children']
    for subR in subreddit:
        print(subR['data']['title'], " ", datetime.fromtimestamp(subR['data']['created_utc']))
    
    # Load the response data to MongoDB
        collection.insert_one(subR['data'])

def auth_api():
    # authenticate API
    auth = requests.auth.HTTPBasicAuth(
        "iYAaR2qDuJgnoBMg45lMIA", "LL5rD1_Iq4tpbnaoRs-JdhUA1imbMA"
    )
    data = {
        "grant_type": "password",
        "username": creds_reddit.username,
        "password": creds_reddit.password,
    }
    headers = {"User-Agent": "MyAPI/0.0.1"}
    # send authentication request for OAuth token
    res = requests.post(
        "https://www.reddit.com/api/v1/access_token",
        auth=auth,
        data=data,
        headers=headers,
    )
    # extract token from response and format correctly
    accessToken = res.json()['access_token']

    # update API headers with authorization (bearer token)
    headers['Authorization'] = f'bearer {accessToken}'
    
    return headers


def scrap_reddit(headers, client, collection):
    try:
        # initialize dataframe and parameters for pulling data in loop
        params = {"limit": 100}
        res = requests.get(
                "https://oauth.reddit.com/r/news/top/?t=hour",
                headers=headers,
                params=params)
        insert_response(res, client, collection)
        res = requests.get(
                "https://oauth.reddit.com/r/politics/top/?t=hour",
                headers=headers,
                params=params)
        insert_response(res, client, collection)
        res = requests.get(
                "https://oauth.reddit.com/r/sports/top/?t=hour",
                headers=headers,
                params=params)
        insert_response(res, client, collection)
        res = requests.get(
                "https://oauth.reddit.com/r/worldnews/top/?t=hour",
                headers=headers,
                params=params)
        insert_response(res, client, collection)
        res = requests.get(
                "https://oauth.reddit.com/r/technology/top/?t=hour",
                headers=headers,
                params=params)
        insert_response(res, client, collection)
    except ValueError as err:
        logging.warning(f"Error - 106: '{err}'")


def main():
    headers = auth_api()
    client, collection = create_server_connection()
    try:
        scrap_reddit(headers, client, collection)
            #for remaining in range(60, 0, -1):
                #sys.stdout.write("\r")
                #sys.stdout.write(
                    #"{:2d} seconds remaining for next Reddit pull".format(remaining)
                #)
                #sys.stdout.flush()
                #time.sleep(1)
                #db = 0
    except ValueError as err:
        logging.warning(f"Error - 94: '{err}'")
    close_server_connection(client)


if __name__ == "__main__":
    main()
