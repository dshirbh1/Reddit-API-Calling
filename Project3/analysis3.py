from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import json
import os
# MongoDB Connection Details
DATABASE_NAME = "social_media_db"
COLLECTION_NAME = "Reddit_Comments_Moderate_Hate_Speech"

def get_data_from_mongodb():
    """
    Connect to MongoDB and retrieve data from the specified collection.
    Returns a pandas DataFrame.
    """
    client = MongoClient("mongodb://localhost:27017/")
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
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
        'Financial': ['finance', 'money', 'economy', 'stock', 'market', 'investment'],
        'Business': ['business', 'company', 'corporate', 'industry', 'enterprise'],
        'Sports': ['sports', 'football', 'basketball', 'soccer', 'tennis', 'olympics'],
        'Arts': ['art', 'music', 'painting', 'dance', 'literature', 'theater', 'film']
    }
    return any(keyword in text.lower() for keyword in keywords.get(category, []))

def plot_graph_for_category(df, category):
    df['is_category'] = df['Response'].apply(lambda x: filter_category(x, category))
    df_category = df[df['is_category']]
    average_confidence_category = df_category.groupby(['Date', 'class'])['confidence'].mean().unstack()

    plt.figure(figsize=(12, 6))
    legend_labels = []

    if 'flag' in average_confidence_category.columns and not average_confidence_category['flag'].isnull().all():
        plt.plot(average_confidence_category['flag'], label='Flag', marker='o')
        legend_labels.append('Flag')

    if 'normal' in average_confidence_category.columns and not average_confidence_category['normal'].isnull().all():
        plt.plot(average_confidence_category['normal'], label='Normal', marker='x')
        legend_labels.append('Normal')

    if legend_labels:
        plt.legend(legend_labels)

    plt.title(f'Average Confidence per Date for Flag and Normal Classes in {category.capitalize()} Comments')
    plt.xlabel('Date')
    plt.ylabel('Average Confidence')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    output_path = 'static/picture/'
    os.makedirs(output_path, exist_ok=True)
    output_file = os.path.join(output_path, 'analysis12.png')
    plt.savefig(output_file)
    #plt.show()

def run_analysis(category):
    df = get_data_from_mongodb()
    #print(df)
    # Parsing JSON strings in the 'ModerateHateSpeech' column
    df['ModerateHateSpeech'] = df['ModerateHateSpeech'].apply(parse_json)
    json_columns = pd.json_normalize(df['ModerateHateSpeech'].dropna())
    df = df.join(json_columns)

    # Converting 'TimeStamp' to datetime and extracting date
    #df['TimeStamp'] = pd.to_datetime(df['TimeStamp'], errors='coerce')
    df['TimeStamp'] = pd.to_datetime(df['TimeStamp'].str.slice(0, 19), format='%Y-%m-%d %H:%M:%S')

    #print(df['TimeStamp']) 
    # Check if the 'TimeStamp' is timezone aware and convert to UTC
    #if df['TimeStamp'].dt.tz is not None:
        #df['TimeStamp'] = df['TimeStamp'].dt.tz_convert('UTC')
    #else:
        #df['TimeStamp'] = df['TimeStamp'].dt.tz_localize(None).dt.tz_convert('UTC')
    
    df['Date'] = df['TimeStamp'].dt.date

    # Ensuring the 'confidence' column is in numeric format
    df['confidence'] = pd.to_numeric(df['confidence'], errors='coerce')

    plot_graph_for_category(df, category)

# This part ensures that the script can be imported without executing the main function
if __name__ == "__main__":
    run_analysis("politics")  # Example category
