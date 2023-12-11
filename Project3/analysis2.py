import plotly
import plotly.express as px
import os

def analysis1_run(topic):
    # Generate the plot
    fig = px.line(x=[1, 2, 3], y=[1, 3, 2], title=topic)

    # Create the directory if it doesn't exist
    output_dir = 'static/plot'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save the plot to an HTML file
    output_file = os.path.join(output_dir, 'analysis1_plot.html')
    fig.write_html(output_file)
