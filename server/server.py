from flask import Flask
from pymongo import MongoClient

app = Flask(__name__)

# The homepage will be a non-interactive visualisation of the current game, with
# a timer. All actions are done through the API.
@app.route('/')
def map():
    return 'This is the map'

# Get the status of the game
@app.route('/status')
def status():
    pass

# Get the token to play as a country
@app.route('/play/<country>')
def play(country):
    pass

# start the game
@app.route('/start')
def start():
    pass

# --- now everything is by country token ---
