"""
Author: Zane Miller
Email: millerzanem@gmail.com
Date: 04/20/2023
Description: Frontend driver for web ui
"""

import keys.db_credentials
from flask import Flask, render_template
from flask_mysqldb import MySQL
from flask_navigation import Navigation

from database.database_dml import *
from models.Comic import Comic

app = Flask(__name__)

#########################################################################################################
#
#                                       DATABASE CONFIGURATION
#
#########################################################################################################
app.config['MYSQL_HOST'] = keys.db_credentials.host
app.config['MYSQL_USER'] = keys.db_credentials.user
app.config['MYSQL_PASSWORD'] = keys.db_credentials.passwd
app.config['MYSQL_DB'] = keys.db_credentials.db
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

#########################################################################################################
#
#                                       NAVBAR CONFIGURATION
#
#########################################################################################################
nav = Navigation(app)
nav.Bar(
    'top', [
        nav.Item('Home', 'index'),
        nav.Item('Comics', 'comics')]
)


def get_comics(comic_id: int = None):
    """ Gets list of all comics and their id, title, issue number, thumbnail """
    cursor = mysql.connection.cursor()

    # get single comic
    if comic_id is not None:
        query = singleComicDetail
        params = (comic_id,)
        cursor.execute(query, params)
        temp_list = [Comic(item) for item in cursor]

        query = singleComicUrls
        params = (comic_id,)
        cursor.execute(query, params)

        for item in cursor:
            temp_list[0].update_attributes(item)

        return temp_list

    # get all purchased comics
    else:
        query = allPurchasedComics
        params = ()
        cursor.execute(query, params)
        return [Comic(item) for item in cursor]


@app.route('/')
def index():
    """ App home page """
    return render_template("home.html")


@app.route('/comics', methods=['GET'])
def comics():
    """ Browse a list of all comics currently in the database """
    comics_data = get_comics()
    return render_template("comics.html", comics_data=comics_data)


@app.route('/view-comic/<int:comic_id>', methods=["GET"])
def view_comic(comic_id):
    """ View individual comic by id """
    comic_data = get_comics(comic_id)[0]
    print(comic_data)
    return render_template("comic_detail.html", comic_data=comic_data)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5011)
