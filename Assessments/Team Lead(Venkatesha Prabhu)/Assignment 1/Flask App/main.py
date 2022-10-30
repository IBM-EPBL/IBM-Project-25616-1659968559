from flask import Flask
import ibm_db
import urllib.parse
from flask_cors import CORS

app=Flask(__name__)
cors=CORS(app)
