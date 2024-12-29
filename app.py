import json
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import requests
import os

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)


