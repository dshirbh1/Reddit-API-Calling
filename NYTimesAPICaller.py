import http.client
import pymongo
import json
import time
from config.config import ConfigMongo

# List of API endpoints
endpoints = {
    "/svc/mostpopular/v2/emailed/7.json?api-key=1exVA9IXsMcGij1FknuCZYFoPIhdC6cl": "emailed",
    "/svc/mostpopular/v2/shared/7/facebook.json?api-key=1exVA9IXsMcGij1FknuCZYFoPIhdC6cl": "shared_facebook",
    "/svc/mostpopular/v2/viewed/30.json?api-key=1exVA9IXsMcGij1FknuCZYFoPIhdC6cl": "viewed",
    "/svc/topstories/v2/world.json?api-key=1exVA9IXsMcGij1FknuCZYFoPIhdC6cl": "top_world",
    "/svc/topstories/v2/politics.json?api-key=1exVA9IXsMcGij1FknuCZYFoPIhdC6cl": "top_politics",
    "/svc/topstories/v2/business.json?api-key=1exVA9IXsMcGij1FknuCZYFoPIhdC6cl": "top_business",
    "/svc/topstories/v2/us.json?api-key=1exVA9IXsMcGij1FknuCZYFoPIhdC6cl": "top_us",
    "/svc/topstories/v2/home.json?api-key=1exVA9IXsMcGij1FknuCZYFoPIhdC6cl": "top_home"
    #"/svc/topstories/v2/sports.json?api-key=1exVA9IXsMcGij1FknuCZYFoPIhdC6cl": "top_sports"
    #"/svc/topstories/v2/science.json?api-key=1exVA9IXsMcGij1FknuCZYFoPIhdC6cl": "top_science"
    #"/svc/topstories/v2/technology.json?api-key=1exVA9IXsMcGij1FknuCZYFoPIhdC6cl": "top_technology"
}

def fetch_data(endpoint, source):
    conn = http.client.HTTPSConnection("api.nytimes.com")
    payload = ''
    headers = {}
    conn.request("GET", endpoint, payload, headers)
    
    res = conn.getresponse()
    data = res.read()
    parsed_data = json.loads(data.decode("utf-8"))
    
    # Adding a source to each entry
    if "results" in parsed_data:
        for entry in parsed_data["results"]:
            entry["source_api"] = source
    
    return parsed_data

def main():
    # Connect to MongoDB
    client = pymongo.MongoClient(ConfigMongo.host, ConfigMongo.port)
    db = client[ConfigMongo.database]
    collection = db[ConfigMongo.collectionNYTimes]
    while True:
        for endpoint, source in endpoints.items():
            data = fetch_data(endpoint, source)
            # Assuming the data is a list of articles or entries
            if "results" in data:
                collection.insert_many(data["results"])
        
        time.sleep(15*60) # Sleep for 15 minutes
    
    client.close()

if __name__ == "__main__":
    main()
