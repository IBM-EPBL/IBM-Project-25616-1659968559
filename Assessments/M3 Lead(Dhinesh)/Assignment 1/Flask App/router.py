from main import app
from flask import request,jsonify,render_template

@app.route("/",methods=["POST","GET"])
def main():
    return render_template("index.html")