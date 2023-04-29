"""
Author: Zane Miller
Email: millerzanem@gmail.com
Date: 04/20/2023
Description: Frontend driver for web ui
"""
import os

from flask import render_template

from app import app
from app.database.db import FrontEndDB

dirname = os.path.dirname(__file__)
f_db = FrontEndDB()


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
    comics_data = f_db.get_purchased_comics()
    return render_template("comics.html", comics_data=comics_data)


@app.route('/view-comic/<int:comic_id>', methods=["GET"])
def view_comic(comic_id):
    """
    View individual comic by id
    :param comic_id: the id of the comic to view details
    :return: render_template("comic_detail.html", comic_data, series_data, story_data, creator_data, event_data,
    character_data, image_data, variant_data)
    """
    comic_detail = f_db.get_single_comic_detail(comic_id)

    series_id = comic_detail.seriesId
    series_detail = {}
    if series_id is not None:
        series_detail = f_db.get_single_series_detail(series_id)
    story_detail = f_db.get_comic_stories(comic_id)
    creators_list = f_db.get_comic_creators(comic_id)
    events_list = f_db.get_comic_events(comic_id)
    character_list = f_db.get_comic_characters(comic_id)
    variant_list = f_db.get_comic_variants(comic_id)
    image_list = f_db.get_comic_images(comic_id)

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


@app.route('/view-comic/<int:comic_id>/update', methods=["GET"])
def update_comic(comic_id):
    """
    Update the comic and its dependencies
    :param comic_id: the id of the comic to update
    :return:
    """

    # create lookup object Lookup(f_db)

    # lookup the comic book (lookup.lookup_marvel_comic_by_id(comic_id) and
    # store complete comic book in backend db (lookup.update_complete_comic_book_byID(comic_id)

    # get comic_has_character ids from backend db
    # lookup.get_comic_has_entity_ids_from_db(lookup.CHARACTER_ENTITY, comic_id)

    # get comic_has_creators ids from backend db
    # lookup.get_comic_has_entity_ids_from_db(lookup.CREATOR_ENTITY, comic_id)

    # get comic_has_events ids from backend db
    # lookup.get_comic_has_entity_ids_from_db(lookup.EVENT_ENTITY, comic_id)

    # get comic_has_series ids from backend db
    # lookup.get_comic_has_entity_ids_from_db(lookup.SERIES_ENTITY, comic_id)

    # get comic_has_stories ids from backend db
    # lookup.get_comic_has_entity_ids_from_db(lookup.STORIES_ENTITY, comic_id)

    # get comic_has_variants ids from backend db
    # lookup.get_comic_has_entity_ids_from_db(lookup.VARIANTS, comic_id)

    # process characters
    # For character in lookup.characters:
    # lookup.lookup_marvel_character_by_id(character)
    # lookup.update_complete_character(character)

    # process creators
    # For creator in lookup.creators:
    # lookup.lookup_marvel_creator_by_id(creator)
    # lookup.update_complete_creator(creator)

    # process events
    # For event in lookup.events:
    # lookup.lookup_marvel_event_by_id(event)
    # lookup.update_complete_event(event)

    # process series
    # For series in lookup.series:
    # lookup.lookup_marvel_series_by_id(series)
    # lookup.update_complete_series(series)

    # process stories
    # For story in lookup.stories:
    # lookup.lookup_marvel_story_by_id(story)
    # lookup.update_complete_story(story)

    # process variants
    # For variant in lookup.variants:
    # lookup.lookup_marvel_variant_by_id(variant)
    # lookup.update_complete_variant(variant)
