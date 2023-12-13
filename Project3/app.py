from flask import Flask, render_template, request, jsonify
# import plot  # Import your analysis logic
# import base64
# from io import BytesIO
import ComparativeAnalysisOverTopic
import DistributionofToxicityScoresforReddit
import DistributionofToxicityScoresforNYTimes
app = Flask(__name__)

@app.route('/')
def index():
    topic = "Politics"
    ComparativeAnalysisOverTopic.ComparativeAnalysis(topic)
    # Get Matplotlib plot from your analysis module
    #return "Hello World"
    DistributionofToxicityScoresforReddit.run_reddit_analysis()
    DistributionofToxicityScoresforNYTimes.run_nytimes_analysis()
    return render_template('index.html', analysis_result=topic)


@app.route('/submit-analysis', methods=['POST'])
def submit_analysis():
    topic = request.form['topic']

    # Call your analysis function with the 'topic' variable
    ComparativeAnalysisOverTopic.ComparativeAnalysis(topic)
    # For example, analysis2.analysis1_run(topic)
    # Save the result and handle as needed
    # return render_template('index.html')  # Pass topic to results template
    DistributionofToxicityScoresforReddit.run_reddit_analysis()
    DistributionofToxicityScoresforNYTimes.run_nytimes_analysis()
    return render_template('index.html', analysis_result=topic)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
