from flask import Flask
from flask_navigation import Navigation

from config import Config

app = Flask(__name__)

nav = Navigation(app)
nav.Bar(
    'top', [
        nav.Item('Home', 'index'),
        nav.Item('Comics', 'comics')]
)
app.config.from_object(Config)
from app.webapp import *
from templates import *

app.run(debug=True, host='0.0.0.0', port=5011)
