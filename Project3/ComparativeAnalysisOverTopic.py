from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import json
import os

# MongoDB Connection Details
REDDIT_DATABASE_NAME = "social_media_db"
REDDIT_COLLECTION_NAME = "Reddit_Comments_Moderate_Hate_Speech"

# MongoDB Connection Details
NYTIMES_DATABASE_NAME = "social_media_db"
NYTIMES_COLLECTION_NAME = "modernhatespeechAPI_NYTimes"

def get_data_from_mongodb(database_name, collection_name):
    client = MongoClient("mongodb://localhost:27017/")
    db = client[database_name]
    collection = db[collection_name]
    data = list(collection.find({}))
    return pd.DataFrame(data)

def parse_json(x):
    if isinstance(x, str):
        try:
            return json.loads(x)
        except ValueError:
            return None
    else:
        return None

def filter_category(text, category):
    keywords = {
        'Politics': ['politics', 'government', 'election', 'democracy', 'republican', 'democrat', 'senate', 'congress'],
        #'Politics': ['politics', 'government', 'election', 'democracy', 'republican', 'democrat', 'senate', 'congress'],
        'Financial': ['finance', 'money', 'economy', 'stock', 'market', 'investment'],
        'Business': ['business', 'company', 'corporate', 'industry', 'enterprise'],
        'Sports': ['sports', 'football', 'basketball', 'soccer', 'tennis', 'olympics'],
        'Arts': ['art', 'music', 'painting', 'dance', 'literature', 'theater', 'film']
    }
    return any(keyword in text.lower() for keyword in keywords.get(category, []))


def process_data(df, category, column):
    # Filter data by category
    df['is_category'] = df[column].apply(lambda x: filter_category(x, category))
    df_category = df[df['is_category']]

    # Group by Date and Class, then calculate the average confidence
    grouped_data = df_category.groupby(['Date', 'class'])['confidence'].mean().reset_index()

    # Rename columns to reflect their content
    grouped_data.rename(columns={'class': 'Class', 'confidence': 'Average Confidence'}, inplace=True)

    return grouped_data

def ComparativeAnalysis(category):
    reddit_df = get_data_from_mongodb(REDDIT_DATABASE_NAME, REDDIT_COLLECTION_NAME)
    reddit_df['TimeStamp'] = pd.to_datetime(reddit_df['TimeStamp'].str.slice(0, 19), format='%Y-%m-%d %H:%M:%S')
    reddit_df['Date'] = reddit_df['TimeStamp'].dt.date
    reddit_df['ModerateHateSpeech'] = reddit_df['ModerateHateSpeech'].apply(parse_json)
    reddit_df = reddit_df.join(pd.json_normalize(reddit_df['ModerateHateSpeech'].dropna()))
    reddit_df['confidence'] = pd.to_numeric(reddit_df['confidence'], errors='coerce')
    reddit_data = process_data(reddit_df, category, 'Response')
    #print(reddit_data)


    nytimes_df = get_data_from_mongodb(NYTIMES_DATABASE_NAME, NYTIMES_COLLECTION_NAME)
    nytimes_df['TimeStamp'] = pd.to_datetime(nytimes_df['timestamp'])
    nytimes_df['Date'] = nytimes_df['TimeStamp'].dt.date
    nytimes_df['confidence'] = pd.to_numeric(nytimes_df['confidence'], errors='coerce')
    nytimes_data = process_data(nytimes_df, category, 'title')
    #print(nytimes_data)

    #plt.figure(figsize=(12, 6))
    #if 'flag' in reddit_data.columns:
    #plt.plot(reddit_data['flag'], label='Reddit Flag', marker='o', color='red')
    #if 'normal' in reddit_data.columns:
    #plt.plot(reddit_data['normal'], label='Reddit Normal', marker='x', color='blue')
    flag_reddit_data = reddit_data[reddit_data['Class'] == 'flag']
    normal_reddit_data = reddit_data[reddit_data['Class'] == 'normal']
    flag_nytimes_data = nytimes_data[nytimes_data['Class'] == 'flag']
    normal_nytimes_data = nytimes_data[nytimes_data['Class'] == 'normal']

    # Plotting
    plt.figure(figsize=(16, 8))
    plt.plot(flag_reddit_data['Date'], flag_reddit_data['Average Confidence'], label='Reddit-Flag', marker='o', color='red')
    plt.plot(normal_reddit_data['Date'], normal_reddit_data['Average Confidence'], label='Reddit-Normal', marker='x', color='blue')
    plt.plot(flag_nytimes_data['Date'], flag_nytimes_data['Average Confidence'], label='NYTimes-Flag', marker='o', color='green')
    plt.plot(normal_nytimes_data['Date'], normal_nytimes_data['Average Confidence'], label='NYTimes-Normal', marker='x', color='black')

    plt.title(f'Average Confidence per Date for {category} in Reddit')
    plt.xlabel('Date')
    plt.ylabel('Average Confidence')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    output_path = 'static/picture/'
    os.makedirs(output_path, exist_ok=True)
    output_file = os.path.join(output_path, f'ComparativeAnalysis.png')
    plt.savefig(output_file)

#if __name__ == "__main__":
    #run_reddit_analysis("Politics")
