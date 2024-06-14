
from flask import jsonify, request
from app import app, mongo

@app.route('/')
def hello_world():
    return jsonify({"about": "Hello, World!"})
