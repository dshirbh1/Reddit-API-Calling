from flask import Flask, render_template
# import base64
import analysis2
# from io import BytesIO

app = Flask(__name__)

@app.route('/')
def index():
    # Get Matplotlib plot from your analysis module
    analysis2.run_analysis2()
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
