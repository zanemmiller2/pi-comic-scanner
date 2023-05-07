import os

from flask import Flask
from flask_mysqldb import MySQL
from flask_navigation import Navigation

app = Flask(__name__)
mysqldb = MySQL(app)
dirname = os.path.dirname(__file__)

nav = Navigation(app)
nav.Bar(
    'top', [
        nav.Item('Home', 'index'),
        nav.Item('Comics', 'comics'),
        nav.Item('Series', 'series')]
)

from config import Config

app.config.from_object(Config)

from app.frontendDatabase.frontendDB import FrontEndDB
from backend.backendDatabase.backendDB import BackEndDB
from backend.classes.lookup_driver import Lookup

f_db = FrontEndDB()
b_db = BackEndDB()
lookup = Lookup(b_db)

from app.views import *
