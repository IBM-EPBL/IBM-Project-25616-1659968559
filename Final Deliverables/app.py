from flask import Flask
import urllib.parse
from flask_cors import CORS

app=Flask(__name__)
app.secret_key = "121212"
cors=CORS(app)
