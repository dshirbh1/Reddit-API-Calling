from flask import Flask, render_template
# import plot  # Import your analysis logic
# import base64
# from io import BytesIO
import analysis2

app = Flask(__name__)

@app.route('/')
def index():
    analysis2.analysis1_run()
    # Get Matplotlib plot from your analysis module
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
