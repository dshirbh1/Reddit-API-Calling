from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os

# MongoDB Connection Details
REDDIT_DATABASE_NAME = "social_media_db"
REDDIT_COLLECTION_NAME = "Reddit_Comments_Moderate_Hate_Speech"

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

def filter_category(text, categories):
    keywords = {
        'Politics': ['politics', 'government', 'election', 'democracy', 'republican', 'democrat', 'senate', 'congress'],
        'Financial': ['finance', 'money', 'economy', 'stock', 'market', 'investment'],
        'Business': ['business', 'company', 'corporate', 'industry', 'enterprise'],
        'Sports': ['sports', 'football', 'basketball', 'soccer', 'tennis', 'olympics'],
        'Arts': ['art', 'music', 'painting', 'dance', 'literature', 'theater', 'film']
        # Add other categories and keywords as needed
    }
    return any(keyword in text.lower() for category in categories for keyword in keywords.get(category, []))

def process_data(df, category, column):
    # Filter data by category
    df['is_category'] = df[column].apply(lambda x: filter_category(x, category))
    df_category = df[df['is_category']]

    # Group by Date and Class, then calculate the average confidence
    grouped_data = df_category.groupby(['Date', 'class'])['confidence'].mean().reset_index()

    # Rename columns to reflect their content
    grouped_data.rename(columns={'class': 'Class', 'confidence': 'Average Confidence'}, inplace=True)

    return grouped_data

def run_reddit_analysis():
    categories = ['Politics', 'Financial', 'Business', 'Sports', 'Arts']
    reddit_df = get_data_from_mongodb(REDDIT_DATABASE_NAME, REDDIT_COLLECTION_NAME)
    reddit_df['TimeStamp'] = pd.to_datetime(reddit_df['TimeStamp'].str.slice(0, 19), format='%Y-%m-%d %H:%M:%S')
    reddit_df['Date'] = reddit_df['TimeStamp'].dt.date
    reddit_df['ModerateHateSpeech'] = reddit_df['ModerateHateSpeech'].apply(parse_json)
    reddit_df = reddit_df.join(pd.json_normalize(reddit_df['ModerateHateSpeech'].dropna()))
    reddit_df['confidence'] = pd.to_numeric(reddit_df['confidence'], errors='coerce')

    plt.figure(figsize=(12, 6))
    for category in categories:
        reddit_data = process_data(reddit_df, [category], 'Response')
        #print(reddit_data)
        flag_reddit_data = reddit_data[reddit_data['Class'] == 'flag']
        #print(flag_reddit_data)
        normal_reddit_data = reddit_data[reddit_data['Class'] == 'normal']
    #flag_nytimes_data = nytimes_data[nytimes_data['Class'] == 'flag']
    #normal_nytimes_data = nytimes_data[nytimes_data['Class'] == 'normal']
        #if 'flag' in reddit_data.columns:
        #sns.lineplot(data=flag_reddit_data, x = flag_reddit_data['Date'], y = flag_reddit_data['Average Confidence'], label=f'Reddit Flag - {category}', marker='o')
        #if 'normal' in reddit_data.columns:
        #sns.lineplot(data=normal_reddit_data['Class'], x = flag_reddit_data['Date'], y = flag_reddit_data['Average Confidence'], label=f'Reddit Normal - {category}', marker='x')
        sns.lineplot(data=flag_reddit_data, x='Date', y='Average Confidence', label=f'Reddit Flag - {category}', marker='o')
        sns.lineplot(data=normal_reddit_data, x='Date', y='Average Confidence', label=f'Reddit Normal - {category}', marker='x')


    plt.title(f'Average Confidence per Date for Reddit in Multiple Categories')
    plt.xlabel('Date')
    plt.ylabel('Average Confidence')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    output_path = 'static/picture/'
    os.makedirs(output_path, exist_ok=True)
    output_file = os.path.join(output_path, 'reddit_analysis_all_categories.png')
    plt.savefig(output_file)

#if __name__ == "__main__":
    #categories_to_analyze = ['Politics', 'Financial', 'Business', 'Sports', 'Arts']
    #run_reddit_analysis(categories_to_analyze)
