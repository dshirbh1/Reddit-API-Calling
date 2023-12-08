import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import pymongo
from config.config import ConfigMongo

#Create a mongoDB connection
def createServerConnection():
    client = pymongo.MongoClient(ConfigMongo.host, ConfigMongo.port)
    db = client[ConfigMongo.database]
    collection = db[ConfigMongo.collectionRedditDates]

    return client, collection

#Close the mongoDB connection
def closeServerConnection(client):
    client.close()

def plotting(collection):


    # Fetch data from MongoDB
    cursor = collection.find()
    df = pd.DataFrame(list(cursor))

    # Convert the datetime column to a datetime type
    df['datetime_column'] = pd.to_datetime(df['dateTime'])
    # Extract the date from the datetime column
    df['date'] = df['datetime_column'].dt.date

    # Count the occurrences of each date
    date_counts = df['date'].value_counts().reset_index()

    # Set a date range
    start_date = pd.to_datetime('2023-11-01').date()
    end_date = pd.to_datetime('2023-11-14').date()

    date_counts = date_counts[(date_counts['date'] >= start_date) & (date_counts['date'] <= end_date)]
    date_counts.columns = ['Date', 'Count']

    # Sort the dates in chronological order
    date_counts = date_counts.sort_values(by='Date')

    # Create a line plot using seaborn
    plt.figure(figsize=(6, 3))
    palette = sns.color_palette("Set2", 13)
    sns.lineplot(data=date_counts, x='Date', y='Count')
    plt.xticks(date_counts['Date'], rotation=90)

    plt.xlabel('Date')
    plt.ylabel('Number of Submissions')

    # Save the plot as an image
    output_path = 'static/picture/'
    os.makedirs(output_path, exist_ok=True)
    output_file = os.path.join(output_path, 'analysis1.png')
    plt.savefig(output_file)

    # Display the plot
    plt.show()

def run_analysis1():
    client, collection = createServerConnection()
    plotting(collection)
    closeServerConnection(client)