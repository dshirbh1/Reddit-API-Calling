import matplotlib.pyplot as plt
import os
def run_analysis2():
    # Sample data
    dates = ['2023-11-01', '2023-11-01', '2023-11-02', '2023-11-02', '2023-11-03']
    keywords = ['technology', 'science', 'technology', 'business', 'science']
    counts = [15, 10, 12, 8, 18]

    # Create a dictionary for mapping keywords to colors
    color_mapping = {'technology': 'blue', 'science': 'green', 'business': 'orange'}

    # Plot using Matplotlib
    plt.figure(figsize=(10, 6))
    for keyword, color in color_mapping.items():
        keyword_counts = [count for d, k, count in zip(dates, keywords, counts) if k == keyword]
        plt.bar(dates, keyword_counts, label=keyword, color=color)

    plt.title('Top Keywords Count Over Time')
    plt.xlabel('Date')
    plt.ylabel('Count')
    plt.legend()
    plt.xticks(rotation=45)

    # Save the plot as an image
    output_path = 'static/picture/'
    os.makedirs(output_path, exist_ok=True)
    output_file = os.path.join(output_path, 'analysis2.png')
    plt.savefig(output_file)

    plt.show()