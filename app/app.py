from typing import List, Dict

import pymysql
from flask import Flask, render_template
from flask_navigation import Navigation

app = Flask(__name__)

nav = Navigation(app)
nav.Bar(
    'top', [
        nav.Item('Home', 'index'),
        nav.Item('Comics', 'comics')]
)


def test_table() -> List[Dict]:
    config = {
        'user': 'zanemiller',
        'password': '230Leafwoodct!',
        'host': '10.0.0.238',
        'port': 3306,
        'database': 'comic_books'
    }
    connection = pymysql.connect(**config)
    cursor = connection.cursor()
    cursor.execute('SELECT id, title FROM Comics')
    results = [{'id': id, 'title': title} for (id, title) in cursor]
    cursor.close()
    connection.close()

    return results


@app.route('/')
def index():
    """ App home page """
    return render_template("index.html")


@app.route('/comics', methods=['GET'])
def comics():
    """ App home page """
    data = test_table()
    return render_template("comics.html", data=data)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5011)
