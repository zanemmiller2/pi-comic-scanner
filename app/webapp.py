"""
Author: Zane Miller
Email: millerzanem@gmail.com
Date: 04/20/2023
Description: Frontend driver for web ui
"""
import os

from flask import render_template

from app import app
from app.database.db import DB

dirname = os.path.dirname(__file__)
db = DB()


#########################################################################################################
#
#                                       DATABASE CONFIGURATION
#
#########################################################################################################


#########################################################################################################
#
#                                       NAVBAR CONFIGURATION
#
#########################################################################################################


@app.route('/')
def index():
    """ App home page """
    return render_template("home.html")


@app.route('/comics', methods=['GET'])
def comics():
    """ Browse a list of all comics currently in the database """
    comics_data = db.get_purchased_comics()
    return render_template("comics.html", comics_data=comics_data)


@app.route('/view-comic/<int:comic_id>', methods=["GET"])
def view_comic(comic_id):
    """ View individual comic by id """
    comic_detail = db.get_single_comic_detail(comic_id)
    print(comic_detail)

    series_id = comic_detail.seriesId
    series_detail = {}
    if series_id is not None:
        series_detail = db.get_single_series_detail(series_id)
    story_detail = db.get_comic_stories(comic_id)
    creators_list = db.get_comic_creators(comic_id)
    events_list = db.get_comic_events(comic_id)
    character_list = db.get_comic_characters(comic_id)
    variant_list = db.get_comic_variants(comic_id)
    image_list = db.get_comic_images(comic_id)
    for character in character_list:
        print(character)

    return render_template(
        "comic_detail.html",
        comic_data=comic_detail,
        series_data=series_detail,
        story_data=story_detail,
        creator_data=creators_list,
        event_data=events_list,
        character_data=character_list,
        variant_data=variant_list,
        image_data=image_list
    )
