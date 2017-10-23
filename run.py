from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    """Default endpoint for API"""
    return 'Welcome to GitHubby API!'
