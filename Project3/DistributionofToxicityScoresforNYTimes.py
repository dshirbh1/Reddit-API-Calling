from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os

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

def run_nytimes_analysis():
    categories = ['Politics', 'Financial', 'Business', 'Sports', 'Arts']
    nytimes_df = get_data_from_mongodb(NYTIMES_DATABASE_NAME, NYTIMES_COLLECTION_NAME)
    nytimes_df['TimeStamp'] = pd.to_datetime(nytimes_df['timestamp'])
    nytimes_df['Date'] = nytimes_df['TimeStamp'].dt.date
    nytimes_df['confidence'] = pd.to_numeric(nytimes_df['confidence'], errors='coerce')

    plt.figure(figsize=(12, 6))
    for category in categories:
        nytimes_data = process_data(nytimes_df, [category], 'title')
        #print(reddit_data)
      
        flag_nytimes_data = nytimes_data[nytimes_data['Class'] == 'flag']
        normal_nytimes_data = nytimes_data[nytimes_data['Class'] == 'normal']
    
        #if 'flag' in reddit_data.columns:
        #sns.lineplot(data=flag_reddit_data, x = flag_reddit_data['Date'], y = flag_reddit_data['Average Confidence'], label=f'Reddit Flag - {category}', marker='o')
        #if 'normal' in reddit_data.columns:
        #sns.lineplot(data=normal_reddit_data['Class'], x = flag_reddit_data['Date'], y = flag_reddit_data['Average Confidence'], label=f'Reddit Normal - {category}', marker='x')
        sns.lineplot(data=flag_nytimes_data, x='Date', y='Average Confidence', label=f'NYTimes Flag - {category}', marker='o')
        sns.lineplot(data=normal_nytimes_data, x='Date', y='Average Confidence', label=f'NYTimes Normal - {category}', marker='x')


    plt.title(f'Average Confidence per Date for NYTimes in Multiple Categories')
    plt.xlabel('Date')
    plt.ylabel('Average Confidence')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    output_path = 'static/picture/'
    os.makedirs(output_path, exist_ok=True)
    output_file = os.path.join(output_path, 'nytimes_analysis_all_categories.png')
    plt.savefig(output_file)

#if __name__ == "__main__":
    #categories_to_analyze = ['Politics', 'Financial', 'Business', 'Sports', 'Arts']
    #run_reddit_analysis(categories_to_analyze)
