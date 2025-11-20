from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)
FEED_SERVICE_URL = 'http://feed_service:8001'

@app.route('/', methods=['GET'])
def index():
    response = requests.get(f'{FEED_SERVICE_URL}/latest')
    prediction = response.json()
    if 'error' not in prediction:
        class_name = prediction['class']
        confidence = prediction['confidence']
        error_message = None
    else:
        class_name = None
        confidence = None
        error_message = prediction['error']

    return render_template('index.html', class_name=class_name, confidence=confidence, error_message=error_message)

@app.route('/trigger', methods=['POST'])
def trigger():
    response = requests.post(f'{FEED_SERVICE_URL}/trigger')

    return redirect(url_for('index'))


@app.route('/image', methods=['GET'])
def image():
    response = requests.get(f'{FEED_SERVICE_URL}/image/latest')
    if response.status_code == 200:
        if response.headers.get('content-type','').startswith('image/'):
            from flask import Response
            return Response(
                response.content,
                mimetype='image/jpeg'
            )
        
    return 'Image not available', 404
