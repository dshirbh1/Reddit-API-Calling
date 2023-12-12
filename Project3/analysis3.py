from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import json
import os

# MongoDB Connection Details
REDDIT_DATABASE_NAME = "social_media_db"
REDDIT_COLLECTION_NAME = "Reddit_Comments_Moderate_Hate_Speech"

NYTIMES_DATABASE_NAME = "social_media_db"
NYTIMES_COLLECTION_NAME = "modernhatespeechAPI_NYTimes"

def get_data_from_mongodb(database_name, collection_name):
    """
    Connect to MongoDB and retrieve data from the specified collection.
    Returns a pandas DataFrame.
    """
    client = MongoClient("mongodb://localhost:27017/")
    db = client[database_name]
    collection = db[collection_name]
    data = list(collection.find({}))
    return pd.DataFrame(data)

def filter_category(text, category, source):
    keywords = {
        'Politics': ['politics', 'government', 'election', 'democracy', 'republican', 'democrat', 'senate', 'congress'],
        'Financial': ['finance', 'money', 'economy', 'stock', 'market', 'investment'],
        'Business': ['business', 'company', 'corporate', 'industry', 'enterprise'],
        'Sports': ['sports', 'football', 'basketball', 'soccer', 'tennis', 'olympics'],
        'Arts': ['art', 'music', 'painting', 'dance', 'literature', 'theater', 'film']
        # Add other categories and keywords as needed
    }
    return any(keyword in text.lower() for keyword in keywords.get(category, []))

def process_data(df, category, column):
    df['is_category'] = df[column].apply(lambda x: filter_category(x, category, column))
    df_category = df[df['is_category']]
    average_confidence_category = df_category.groupby(['Date', 'class'])['confidence'].mean().unstack()
    return average_confidence_category

def run_combined_analysis(category):
    # Fetching and processing Reddit data
    reddit_df = get_data_from_mongodb(REDDIT_DATABASE_NAME, REDDIT_COLLECTION_NAME)
    reddit_df['TimeStamp'] = pd.to_datetime(reddit_df['TimeStamp'].str.slice(0, 19), format='%Y-%m-%d %H:%M:%S')
    reddit_df['Date'] = reddit_df['TimeStamp'].dt.date
    reddit_df['ModerateHateSpeech'] = reddit_df['ModerateHateSpeech'].apply(parse_json)
    reddit_df = reddit_df.join(pd.json_normalize(reddit_df['ModerateHateSpeech'].dropna()))
    reddit_df['confidence'] = pd.to_numeric(reddit_df['confidence'], errors='coerce')
    reddit_data = process_data(reddit_df, category, 'Response')

    # Fetching and processing NYTimes data
    nytimes_df = get_data_from_mongodb(NYTIMES_DATABASE_NAME, NYTIMES_COLLECTION_NAME)
    nytimes_df['TimeStamp'] = pd.to_datetime(nytimes_df['timestamp'])
    nytimes_df['Date'] = nytimes_df['TimeStamp'].dt.date
    # nytimes_df['ModerateHateSpeech'] = nytimes_df['ModerateHateSpeech'].apply(parse_json)
    # nytimes_df = nytimes_df.join(pd.json_normalize(nytimes_df['ModerateHateSpeech'].dropna()))
    nytimes_df['confidence'] = pd.to_numeric(nytimes_df['confidence'], errors='coerce')
    nytimes_data = process_data(nytimes_df, category, 'Title')

    # Merging and plotting data
    plt.figure(figsize=(12, 6))
    if 'flag' in reddit_data.columns:
        plt.plot(reddit_data['flag'], label='Reddit Flag', marker='o', color='red')
    if 'normal' in reddit_data.columns:
        plt.plot(reddit_data['normal'], label='Reddit Normal', marker='x', color='blue')
    if 'flag' in nytimes_data.columns:
        plt.plot(nytimes_data['flag'], label='NYTimes Flag', marker='^', color='green')
    if 'normal' in nytimes_data.columns:
        plt.plot(nytimes_data['normal'], label='NYTimes Normal', marker='s', color='purple')

    plt.title(f'Average Confidence per Date for Flag and Normal Classes in {category} - Reddit vs NYTimes')
    plt.xlabel('Date')
    plt.ylabel('Average Confidence')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    output_path = 'static/picture/'
    os.makedirs(output_path, exist_ok=True)
    output_file = os.path.join(output_path, f'combined_analysis_{category}.png')
    plt.savefig(output_file)

if __name__ == "__main__":
    run_combined_analysis("Politics")
