"""
Author: Zane Miller
Email: millerzanem@gmail.com
Date: 04/17/2023
Description: Class drivers for looking up marvel comics with marvel public api
"""
import hashlib
import time

import requests as requests

from code.classes.lookup_driver import COMICS_URL
from keys.private_keys import marvel_developer_priv_key
from keys.pub_keys import marvel_developer_pub_key


class ComicBook:

    def __init__(self, db_connection):
        """ Represents a Comic book based on the marvel comic developer api json response model """
        self.db = db_connection
        self.data = None
        self.count = None  # int, optional

        self.id = None  # int, optional
        self.digitalId = None  # int, optional
        self.title = ""  # string, optional
        self.issueNumber = None  # double, optional
        self.variantDescription = ""  # string, optional
        self.description = ""  # string, optional
        self.modified = None  # Date, optional
        self.isbn = ""  # string, optional
        self.upc = ""  # string, optional
        self.diamondCode = ""  # string, optional
        self.ean = ""  # string, optional
        self.issn = ""  # string, optional
        self.format = ""  # string, optional
        self.pageCount = None  # int, optional
        self.textObjects = {}  # Array[TextObject], optional
        # self.textObjects[type] = {
        #     'language': string, optional,
        #     'text': string, optional
        # }
        self.resourceURI = ""  # string, optional
        self.urls = []
        self.seriesId = None
        self.variantIds = []
        self.onsaleDate = ""
        self.focDate = ""
        self.unlimitedDate = ""
        self.digitalPurchaseDate = ""
        self.printPrice = None
        self.digitalPurchasePrice = None
        self.thumbnail = ""
        self.images = []
        self.creatorIds = {}  # Array[Creators], optional (self.creators = {creator_id : [roles]})
        self.characterIds = []  # Array[CharactersIds], optional
        self.storyIds = []  # Array[StoriesIds], optional
        self.eventIds = []  # Array[Events], optional

    def temp_get_json_res(self):
        """
        DOCSTRING
        """
        timestamp = int(time.time())
        input_string = str(
            str(timestamp)
            + marvel_developer_priv_key
            + marvel_developer_pub_key
        )

        hash_str, timestamp = hashlib.md5(input_string.encode("utf-8")).hexdigest(), timestamp
        barcode = "75960609724101711"
        upc_code = barcode
        PARAMS = {
            'apikey': marvel_developer_pub_key, 'ts': timestamp, 'hash': hash_str, 'upc': upc_code
        }
        request = requests.get(COMICS_URL, PARAMS)
        data = request.json()

        if data['data']['count'] == 0:
            print(f"No comics found with {upc_code} upc")

        elif data['data']['count'] > 1:
            print("MORE THAN ONE COMIC FOUND!!!!!!!!!!!")
        else:
            self.data = data['data']['results'][0]

        print(self.data)

    def save_id(self):
        """
        The unique ID of the comic resource.
        """
        self.id = int(self.data['id'])

    def save_digitalId(self):
        """
        The ID of the digital comic representation of this comic.
        Will be 0 if the comic is not available digitally.
        """
        self.digitalId = int(self.data['digitalId'])

    def save_title(self):
        """
        The canonical title of the comic.
        """
        self.title = str(self.data['title'])

    def save_issueNumber(self):
        """
        The number of the issue in the series (will generally be 0 for collection formats).
        """
        self.issueNumber = float(self.data['issueNumber'])

    def save_variantDescription(self):
        """
        If the issue is a variant (e.g. an alternate cover, second printing, or director’s cut),
        a text description of the variant.
        """
        self.variantDescription = str(self.data['variantDescription'])

    def save_description(self):
        """
        The preferred description of the comic.
        """
        self.description = str(self.data['description'])

    def save_modified(self):
        """
        The date the resource was most recently modified.
        """
        self.modified = str(self.data['modified'])

    def save_isbn(self):
        """
        The ISBN for the comic (generally only populated for collection formats).
        """
        self.isbn = str(self.data['isbn'])

    def save_upc(self):
        """
        The UPC barcode number for the comic (generally only populated for periodical formats).
        """
        self.upc = str(self.data['upc'])

    def save_diamondCode(self):
        """
        The Diamond Code for the comic.
        """
        self.diamondCode = str(self.data['diamondCode'])

    def save_ean(self):
        """
        The EAN barcode for the comic.
        """
        self.ean = str(self.data['ean'])

    def save_issn(self):
        """
        The ISSN barcode for the comic.
        """
        self.issn = str(self.data['issn'])

    def save_format(self):
        """
        The publication format of the comic e.g. comic, hardcover, trade paperback.
        """
        self.format = str(self.data['format'])

    def save_pageCount(self):
        """
        The number of story pages in the comic.
        """
        self.pageCount = int(self.data['pageCount'])

    def save_textObjects(self):
        """
        A set of descriptive text blurbs for the comic.
        """
        for text_obj in self.data['textObjects']:
            textObjectType = ""
            language = ""
            text = ""

            if 'type' in text_obj:
                textObjectType = str(text_obj['type'])
            if 'language' in text_obj:
                language = str(text_obj['language'])
            if 'text' in text_obj:
                text = str(text_obj['text'])

            if textObjectType not in self.textObjects:
                self.textObjects[textObjectType] = [{'language': language, 'text': text}]
            else:
                self.textObjects[textObjectType].append({'language': language, 'text': text})

    def save_resourceURI(self):
        """
        The canonical URL identifier for this resource.
        """
        self.resourceURI = str(self.data['resourceURI'])

    def save_dates(self):
        """
        A list of key dates for this comic.
        """
        for date in self.data['dates']:
            if date['type'] == "onsaleDate":
                self.onsaleDate = date['date']
            elif date['type'] == "focDate":
                self.focDate = date['date']
            elif date['type'] == "unlimitedDate":
                self.unlimitedDate = date['date']
            elif date['type'] == "digitalPurchaseDate":
                self.digitalPurchaseDate = date['date']
            else:
                print(f"{date['type']} DATE TYPE NOT CATEGORIZED")

    def save_prices(self):
        """
        A list of prices for this comic.
        """

        for price in self.data['prices']:
            if price['type'] == 'printPrice':
                self.printPrice = float(price['price'])
            elif price['type'] == 'digitalPurchasePrice':
                self.digitalPurchasePrice = float(price['price'])
            else:
                print(f"{price['type']} PRICE TYPE NOT CATEGORIZED")

    #################################################################
    #                NEED TO IMPLEMENT (GETTERS)
    #################################################################
    def get_originalIssue(self):
        """
        Finds the id of the original issue if comic is a variant
        """
        pass

    #################################################################
    #                NEED TO IMPLEMENT (SAVERS)
    #################################################################
    def save_images(self):
        """
        A list of promotional images associated with this comic.
        """
        # TODO

        # For each image in images and thumbnail:
        # if image not in comic_books.images table:
        # add full image path to images
        # add image to list of images -- will later be used to create Comics_has_Images

        pass

    def save_thumbnail(self):
        """
        The representative image for this comic.
        """

        # TODO

        # Check if thumbnail is in images table
        # add it if not already there
        # add image path to member variable
        pass

    def save_creators(self):
        """
        A resource list containing the creators associated with this comic.
        """

        # TODO

        # For each creator:
        # get creator id
        # get creator first name
        # get creator last name
        # if creator is not in Creators DB
        # Add new creator with resourceURI, id, first name, last name

        # save creator id: role -- will later be used to create Comics_has_Creators entry

        pass

    def save_characters(self):
        """
        A resource list containing the characters which appear in this comic.
        """

        # TODO

        # For each character:
        # Get character ID
        # get character full name

        # if character not in db:
        # add character with resourceURI, name, id

        # save character_id to list -- will later be used to create Comics_has_Characters entry

        pass

    def save_stories(self):
        """
        A resource list containing the stories which appear in this comic.
        """

        # TODO

        # For each story type:
        # Get story ID
        # get story Name
        # get story Type

        # If story not in stories table:
        # Add to table with resourceURI, name, type, id

        # add story id to list -- will later be used to create Comics_has_Stories entry

        pass

    def save_events(self):
        """
        A resource list containing the events in which this comic appears.
        """

        # TODO

        # For each event:
        # Get event ID
        # Get event name

        # If event not in events table:
        # Add event with id, resourceURI, name

        # Save eventID to list -- will later be used to create Comics_has_Events entry

    def save_urls(self):
        """
        A set of public web-site URLs for the resource.
        """
        # TODO

        # For each URL:
        # If url not in comic_books.urls -- add type and url to urls table
        # add to comic_urls list -- later will be used to create Comics_has_URLs relationship

        pass

    def save_series(self):
        """
        A set of public web-site URLs for the resource.,
        """
        # TODO

        # Get series ID (strip from resourceURI)
        # Check if series id in comic_books.series table
        # If series id is not already in db: add to db with id, resourceURI, and name
        pass

    def save_variants(self):
        """
        A list of variant issues for this comic
        (includes the "original" issue if the current issue is a variant).
        """
        # TODO

        # for each variant:
        # Get the comic id of the variant
        # check if id in comics table
        # if not in comics table:
        # add to comics table with id, resourceURI, name
        # add variant ID to list -- later will be used to update Comics_has_Variants

        pass

    #################################################################
    #       NEED TO IMPLEMENT (Comics_has_* relations)
    #################################################################

    def comics_has_characters(self):
        """
        DOCSTRING
        """
        pass

    def comics_has_creators(self):
        """
        DOCSTRING
        """
        pass

    def comics_has_stories(self):
        """
        DOCSTRING
        """
        pass

    def comics_has_events(self):
        """
        DOCSTRING
        """
        pass

    def comics_has_variants(self):
        """
        DOCSTRING
        """
        pass

    def comics_has_images(self):
        """
        DOCSTRING
        """
        pass

    def comics_has_urls(self):
        """
        DOCSTRING
        """
        pass

    #################################################################
    #       NEED TO IMPLEMENT (intermediate entries)
    #################################################################
    def add_new_series(self):
        """
        DOCSTRING
        """
        pass

    def add_new_url(self):
        """
        DOCSTRING
        """
        pass

    def add_new_creator(self):
        """
        DOCSTRING
        """
        pass

    def add_new_story(self):
        """
        DOCSTRING
        """
        pass

    def add_new_image(self):
        """
        DOCSTRING
        """
        pass

    def add_new_variant(self):
        """
        DOCSTRING
        """
        pass

    def add_new_event(self):
        """
        DOCSTRING
        """
        pass

    def add_new_character(self):
        """
        DOCSTRING
        """
        pass


if __name__ == '__main__':
    cb = ComicBook()
    cb.temp_get_json_res()
