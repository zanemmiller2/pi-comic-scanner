"""
Author: Zane Miller
Email: millerzanem@gmail.com
Date: 04/20/2023
Description: Frontend driver for web ui
"""
import os

from flask import render_template, redirect, request, url_for

from app import app, f_db, lookup

dirname = os.path.dirname(__file__)


@app.route('/')
def index():
    """ App home page """
    return render_template("home.html")


@app.route('/comics', methods=['GET'])
def comics():
    """ Browse a list of all comics currently in the frontendDatabase """
    comics_data = f_db.get_purchased_comics()
    return render_template("comics.html", comics_data=comics_data)


@app.route('/view/<int:comic_id>', methods=["GET"])
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
    story_detail = f_db.get_comic_stories(comic_id)[0]
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


def _update_comic_helper(comic_id):
    """
    Driver function for updating a comic and each of its entity dependencies
    :param comic_id: the id of the comic to update
    """

    # create lookup object Lookup(f_db)
    lookup.comic_books[comic_id] = None

    # lookup the comic book (lookup.lookup_marvel_comic_by_id(comic_id) and
    lookup.lookup_marvel_comic_by_id(comic_id)
    # store complete comic book in backend db (lookup.update_complete_comic_book_byID(comic_id)
    lookup.update_complete_comic_book_byID(comic_id)

    # get comic_has_entity ids from backend db
    lookup.get_comic_has_entity_ids_from_db(lookup.CHARACTER_ENTITY, comic_id)
    lookup.get_comic_has_entity_ids_from_db(lookup.CREATOR_ENTITY, comic_id)
    lookup.get_comic_has_entity_ids_from_db(lookup.EVENT_ENTITY, comic_id)
    lookup.get_comic_has_entity_ids_from_db(lookup.SERIES_ENTITY, comic_id)
    lookup.get_comic_has_entity_ids_from_db(lookup.STORY_ENTITY, comic_id)
    lookup.get_comic_has_entity_ids_from_db(lookup.VARIANT_ENTITY, comic_id)

    # process each entity
    for character_id in lookup.characters:
        lookup.lookup_marvel_character_by_id(character_id)
    for character_id in lookup.characters:
        lookup.update_complete_character(character_id)

    for creator_id in lookup.creators:
        lookup.lookup_marvel_creator_by_id(creator_id)
    for creator_id in lookup.creators:
        lookup.update_complete_creator(creator_id)

    for event_id in lookup.events:
        lookup.lookup_marvel_event_by_id(event_id)
    for event_id in lookup.events:
        lookup.update_complete_event(event_id)

    for series_id in lookup.series:
        lookup.lookup_marvel_series_by_id(series_id)
    for series_id in lookup.series:
        lookup.update_complete_series(series_id)

    for story_id in lookup.stories:
        lookup.lookup_marvel_story_by_id(story_id)
    for story_id in lookup.stories:
        lookup.update_complete_story(story_id)

    for variant_id in lookup.variants:
        lookup.lookup_marvel_variant_by_id(variant_id)
    for variant_id in lookup.variants:
        lookup.update_complete_variant(variant_id)


@app.route('/refresh/<int:comic_id>', methods=["GET"])
def update_comic(comic_id):
    """
    Update the comic and its dependencies
    :param comic_id: the id of the comic to update
    :return:
    """
    if request.method == 'GET':
        _update_comic_helper(comic_id)

        return redirect(url_for('view_comic', comic_id=comic_id))

