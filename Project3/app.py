from flask import Flask, render_template, request, jsonify
# import plot  # Import your analysis logic
# import base64
# from io import BytesIO
import analysis2

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    topic = "Politics"
    analysis2.analysis1_run(topic)
    # Get Matplotlib plot from your analysis module
    return render_template('index.html', analysis_result=topic)


@app.route('/submit-analysis', methods=['POST'])
def submit_analysis():
    topic = request.form['topic']

    # Call your analysis function with the 'topic' variable
    analysis2.analysis1_run(topic)
    # For example, analysis2.analysis1_run(topic)
    # Save the result and handle as needed
    # return render_template('index.html')  # Pass topic to results template
    return render_template('index.html', analysis_result=topic)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
