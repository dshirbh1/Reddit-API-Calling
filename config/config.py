class ConfigReddit:
    username = "dshirbh8"
    password = "SocialMedia"
creds_reddit = ConfigReddit()

class ConfigMongo:
    host = "128.226.29.107:27017"
    port = 27017
    database = "social_media_db"
    collectionRedditDates = "Reddit_Dates"
    collectionCommentsHour = "Reddit_Comments_Hour"
creds_mongodb = ConfigMongo()