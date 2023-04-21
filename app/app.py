"""
Author: Zane Miller
Email: millerzanem@gmail.com
Date: 04/20/2023
Description: Frontend driver for web ui
"""

from flask import Flask, render_template, redirect
from flask_mysqldb import MySQL
from flask_navigation import Navigation

import keys.db_credentials
from Comic import Comic

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


def get_comics():
    """ Gets list of all comics and their id, title, issue number, thumbnail """
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM Comics ORDER BY title;"
    cursor.execute(query)
    results = [Comic(item) for item in cursor]

    return results


def get_comic_by_id(comic_id):
    """
    Querys the database and returns the comic by id
    :param comic_id:
    :return:
    """
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM Comics WHERE id=%s;"
    params = (comic_id,)
    cursor.execute(query, params)
    data = cursor.fetchall()[0]
    comic = Comic(data)
    print(comic.title)


@app.route('/')
def index():
    """ App home page """
    return render_template("home.html")


@app.route('/comics', methods=['GET'])
def comics():
    """ Browse a list of all comics currently in the database """
    data = get_comics()
    return render_template("comics.html", comics_data=data)


@app.route('/view-comic/<int:comic_id>', methods=["GET"])
def view_comic(comic_id):
    """ View individual comic by id """
    get_comic_by_id(comic_id)
    return redirect('/comics')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5011)
