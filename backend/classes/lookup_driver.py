"""
Author: Zane Miller
Email: millerzanem@gmail.com
Date: 04/16/2023
Description: Driver class for looking up scanned_barcodes
"""
import hashlib
import time

import keys.private_keys
import keys.pub_keys
import requests

from backend.models.Characters import Character
from backend.models.ComicBook import ComicBook
from backend.models.Creators import Creator
from backend.models.Events import Event
from backend.models.Series import Series
from backend.models.Stories import Story
from backend.models.Variants import Variant


class Lookup:
    """ Lookup object responsible for looking up queued_barcodes in scanned upc buffer """

    CHARACTER_ENTITY = "Characters"
    COMIC_ENTITY = "Comics"
    CREATOR_ENTITY = "Creators"
    EVENT_ENTITY = "Events"
    IMAGE_ENTITY = "Images"
    SERIES_ENTITY = "Series"
    STORY_ENTITY = "Stories"
    URL_ENTITY = "URLs"
    VARIANT_ENTITY = "Variants"
    PURCHASED_COMICS_ENTITY = 'PurchasedComics'
    ENTITIES = {CHARACTER_ENTITY, COMIC_ENTITY, CREATOR_ENTITY, EVENT_ENTITY, IMAGE_ENTITY,
                SERIES_ENTITY, STORY_ENTITY, URL_ENTITY, PURCHASED_COMICS_ENTITY, VARIANT_ENTITY}
    COMIC_DEPENDENCIES = {CHARACTER_ENTITY, CREATOR_ENTITY, EVENT_ENTITY, SERIES_ENTITY, STORY_ENTITY, VARIANT_ENTITY}
    COMICS_URL = "https://gateway.marvel.com/v1/public/comics"
    CHARACTERS_URL = "https://gateway.marvel.com/v1/public/characters"
    CREATORS_URL = "https://gateway.marvel.com/v1/public/creators"
    EVENTS_URL = "https://gateway.marvel.com/v1/public/events"
    SERIES_URL = "https://gateway.marvel.com/v1/public/series"
    STORIES_URL = "https://gateway.marvel.com/v1/public/stories"
    MARVEL_YYYY_MM_DD_SUFFIX = "T00:00:00-0400"

    def __init__(self, lookup_db):
        """
        Object represents a lookup object with a dictionary of barcodes, comic books and a db connection
        """
        self.queued_barcodes = {}  # (queued_barcodes[barcode] = {prefix: barcode_prefix, upload_date: ''})
        self.lookedUp_barcodes = {}  # (lookedUp_barcodes[barcode] = {cb: comic_books[barcode], prefix: ''})
        self.committed_barcodes = {}  # (committed_barcodes[barcode] = {cb: comic_books[barcode], prefix: ''})

        self.comic_books = {}  # (comic_books[barcode] = ComicBook())
        self.creators = {}  # (creators[creatorId] = Creator())
        self.series = {}  # (series[seriesId] = Series())
        self.stories = {}  # (stories[storyId] = Story())
        self.characters = {}  # (characters[characterId] = Character())
        self.events = {}  # (events[eventId] = Event())
        self.variants = {}  # (variants[variantId] = Comic())

        self.db = lookup_db
        self.LOOKUP_DEBUG = True

    ####################################################################################################################
    #
    #                                           HTTPS INTERACTIONS
    #
    ####################################################################################################################
    def lookup_marvel_character_by_id(self, character_id: int):
        """
        Pulls Character information from CHARACTERS_URL + '/{characterId}'
        :param character_id: the integer id of the character resource
        """

        if character_id in self.characters:
            hash_str, timestamp = self._get_marvel_api_hash()

            PARAMS = {'apikey': keys.pub_keys.marvel_developer_pub_key, 'ts': timestamp, 'hash': hash_str}
            endpoint = self.CHARACTERS_URL + '/' + str(character_id)

            request = requests.get(endpoint, PARAMS)
            data = request.json()

            if data['code'] == 200:
                if data['data']['count'] == 0:
                    print(f"No Characters found with {character_id} character id") if self.LOOKUP_DEBUG else 0
                elif data['data']['count'] > 1:
                    print("TOO MANY CHARACTERS FOUND...") if self.LOOKUP_DEBUG else 0
                else:
                    self._make_character_object(data['data']['results'][0], character_id)
            elif data['code'] == 404:
                print(data['status'])
            else:
                print(f"UNKNOWN ERROR RESPONSE CODE {data['code']}")

    def lookup_marvel_comic_by_upc(self, barcode: str):
        """
        Sends the http request to /comics&upc= endpoint and store response as comic_books object
        :param barcode: the upc barcode for the comic to look up
        """

        # barcode has not already been lookedUp
        if barcode not in self.lookedUp_barcodes:
            hash_str, timestamp = self._get_marvel_api_hash()

            PARAMS = {
                    'apikey': keys.pub_keys.marvel_developer_pub_key, 'ts': timestamp, 'hash': hash_str, 'upc': barcode
            }
            request = requests.get(self.COMICS_URL, PARAMS)
            data = request.json()

            if data['data']['count'] == 0:
                print(f"No comics found with {barcode} upc") if self.LOOKUP_DEBUG else 0
            elif data['data']['count'] > 1:
                print("TOO MANY COMIC BOOKS FOUND...") if self.LOOKUP_DEBUG else 0
            else:
                self._make_comic_book_object_byUPC(data['data']['results'][0], barcode)
        else:
            print("BARCODE HAS ALREADY BEEN LOOKED UP...WAITING TO BE COMMITTED") if self.LOOKUP_DEBUG else 0

    def lookup_marvel_comic_by_id(self, comic_id: int):
        """
        Pulls Comic information from COMICS_URL + '/{comicId}'
        :param comic_id: the integer id of the comic resource
        """

        if comic_id in self.comic_books:
            hash_str, timestamp = self._get_marvel_api_hash()

            PARAMS = {'apikey': keys.pub_keys.marvel_developer_pub_key, 'ts': timestamp, 'hash': hash_str}
            endpoint = self.COMICS_URL + '/' + str(comic_id)

            request = requests.get(endpoint, PARAMS)
            data = request.json()

            if data['code'] == 200:
                if data['data']['count'] == 0:
                    print(f"No Comics found with {comic_id} comic id") if self.LOOKUP_DEBUG else 0
                elif data['data']['count'] > 1:
                    print("TOO MANY COMICS FOUND...") if self.LOOKUP_DEBUG else 0
                else:
                    self._make_comic_book_object_byID(data['data']['results'][0], comic_id)
            elif data['code'] == 404:
                print(data['status'])
            else:
                print(f"UNKNOWN ERROR RESPONSE CODE {data['code']}")

    def lookup_marvel_creator_by_id(self, creator_id: int):
        """
        Pulls creator information from CREATORS_URL + '/{creatorId}'
        :param creator_id: the integer id of the creator resource
        """

        if creator_id in self.creators:
            hash_str, timestamp = self._get_marvel_api_hash()

            PARAMS = {'apikey': keys.pub_keys.marvel_developer_pub_key, 'ts': timestamp, 'hash': hash_str}
            endpoint = self.CREATORS_URL + '/' + str(creator_id)

            request = requests.get(endpoint, PARAMS)
            data = request.json()

            if data['code'] == 200:
                if data['data']['count'] == 0:
                    print(f"No Creator found with {creator_id} creator id") if self.LOOKUP_DEBUG else 0
                elif data['data']['count'] > 1:
                    print("TOO MANY CREATORS FOUND...") if self.LOOKUP_DEBUG else 0
                else:
                    self._make_creator_object(data['data']['results'][0], creator_id)
            elif data['code'] == 404:
                print(data['status'])
            else:
                print(f"UNKNOWN ERROR RESPONSE CODE {data['code']}")

    def lookup_marvel_event_by_id(self, event_id: int):
        """
        Pulls Event information from EVENTS_URL + '/{eventId}'
        :param event_id: the integer id of the event resource
        """

        if event_id in self.events:
            hash_str, timestamp = self._get_marvel_api_hash()

            PARAMS = {'apikey': keys.pub_keys.marvel_developer_pub_key, 'ts': timestamp, 'hash': hash_str}
            endpoint = self.EVENTS_URL + '/' + str(event_id)

            request = requests.get(endpoint, PARAMS)
            data = request.json()
            if data['code'] == 200:
                if data['data']['count'] == 0:
                    print(f"No Events found with {event_id} event id") if self.LOOKUP_DEBUG else 0
                elif data['data']['count'] > 1:
                    print("TOO MANY EVENTS FOUND...") if self.LOOKUP_DEBUG else 0
                else:
                    self._make_event_object(data['data']['results'][0], event_id)
            elif data['code'] == 404:
                print(data['status'])
            else:
                print(f"UNKNOWN ERROR RESPONSE CODE {data['code']}")

    def lookup_marvel_series_by_id(self, series_id: int):
        """
        Pulls series information from SERIES_URL + '/{seriesId}'
        :param series_id: the integer id of the series resource
        """

        if series_id in self.series:
            hash_str, timestamp = self._get_marvel_api_hash()

            PARAMS = {'apikey': keys.pub_keys.marvel_developer_pub_key, 'ts': timestamp, 'hash': hash_str}
            endpoint = self.SERIES_URL + '/' + str(series_id)

            request = requests.get(endpoint, PARAMS)
            data = request.json()

            if data['code'] == 200:
                if data['data']['count'] == 0:
                    print(f"No Series found with {series_id} series id") if self.LOOKUP_DEBUG else 0
                elif data['data']['count'] > 1:
                    print("TOO MANY SERIES FOUND...") if self.LOOKUP_DEBUG else 0
                else:
                    self._make_series_object(data['data']['results'][0], series_id)
            elif data['code'] == 404:
                print(data['status'])
            else:
                print(f"UNKNOWN ERROR RESPONSE CODE {data['code']}")

    def lookup_marvel_story_by_id(self, story_id: int):
        """
        Pulls story information from STORIES_URL + '/{storyId}'
        :param story_id: the integer id of the story resource
        """

        if story_id in self.stories:
            hash_str, timestamp = self._get_marvel_api_hash()

            PARAMS = {'apikey': keys.pub_keys.marvel_developer_pub_key, 'ts': timestamp, 'hash': hash_str}
            endpoint = self.STORIES_URL + '/' + str(story_id)

            request = requests.get(endpoint, PARAMS)
            data = request.json()

            if data['code'] == 200:
                if data['data']['count'] == 0:
                    print(f"No Stories found with {story_id} story id") if self.LOOKUP_DEBUG else 0
                elif data['data']['count'] > 1:
                    print("TOO MANY STORIES FOUND...") if self.LOOKUP_DEBUG else 0
                else:
                    self._make_story_object(data['data']['results'][0], story_id)
            elif data['code'] == 404:
                print(data['status'])
            else:
                print(f"UNKNOWN ERROR RESPONSE CODE {data['code']}")

    def lookup_marvel_variant_by_id(self, variant_id: int):
        """
        Pulls Comic information from COMICS_URL + '/{comicId}'
        :param variant_id: the integer id of the comic resource
        """

        if variant_id in self.variants:
            hash_str, timestamp = self._get_marvel_api_hash()

            PARAMS = {'apikey': keys.pub_keys.marvel_developer_pub_key, 'ts': timestamp, 'hash': hash_str}
            endpoint = self.COMICS_URL + '/' + str(variant_id)

            request = requests.get(endpoint, PARAMS)
            data = request.json()

            if data['code'] == 200:
                if data['data']['count'] == 0:
                    print(f"No Variant found with {variant_id} variant id") if self.LOOKUP_DEBUG else 0
                elif data['data']['count'] > 1:
                    print("TOO MANY VARIANTS FOUND...") if self.LOOKUP_DEBUG else 0
                else:
                    self._make_variant_object(data['data']['results'][0], variant_id)
            elif data['code'] == 404:
                print(data['status'])
            else:
                print(f"UNKNOWN ERROR RESPONSE CODE {data['code']}")

    ####################################################################################################################
    #
    #                                       OBJECT INTERACTIONS
    #
    ####################################################################################################################

    ################################################################
    #  MAKE CHARACTERS
    ################################################################
    def _make_character_object(self, marvel_character_data, character_id: int):
        """
        Create a Character() object with the api response data and the character_id
        :param marvel_character_data: json response from the marvel lookup api
        :param character_id: id of the character
        """

        # establish a connection with the Character() object and pass database control to the Character() object
        characterObj = Character(self.db, marvel_character_data)

        # Saves the character objects to its member variables
        characterObj.save_properties()

        # link the characterObj to the appropriate character_id
        self.characters[character_id] = characterObj

    def update_complete_character(self, character_id: int):
        """
        Create a new database record for the looked up Character() Object. First uploads any non-existent foreign key
        dependencies and then uploads the entire Character object.
        :param character_id: character's identification number
        """

        # Valid creator id
        if character_id in self.characters:
            # Create new records for the different member variables that also represent database entities.
            # For example, create a new series if it does not already exist so that the Story() storyId
            # foreign key dependency can be established.
            self.characters[character_id].upload_new_records()

            # Once all the foreign key dependencies have been established, go ahead and create the
            # Character entity with all of its foreign key dependencies
            self.characters[character_id].upload_character()

            # Once the Character() has been uploaded, go ahead and create the entity_has_relationships
            self.characters[character_id].upload_character_has_relationships()

        else:
            print(f"INVALID CHARACTER ID {character_id}...") if self.LOOKUP_DEBUG else 0

    ################################################################
    #  MAKE COMIC
    ################################################################

    def get_purchased_details(self, marvel_comic_data) -> tuple[str, float, str]:
        """ Gets the purchase details from the user """

        purchasedDate = None
        purchasedPrice = None

        # Purchased type
        purchasedType_res = input("Purchase Format:\n(1) Print\n(2) Digital\n> ")
        if purchasedType_res == '1' or purchasedType_res == '2':
            if purchasedType_res == '1':
                purchasedType = "Comic"
                dateType = 'onsaleDate'
                priceType = 'printPrice'
            else:
                purchasedType = "Digital"
                dateType = 'digitalPurchaseDate'
                priceType = 'digitalPurchasePrice'

            # Purchased Date
            for date in marvel_comic_data['dates']:
                if date['type'] == dateType:
                    purchasedDate = date['date']
                    break
            purchasedDate_res = input(f"Purchased Date:\n(1) {purchasedDate}\n(2) Enter different date?\n> ")
            if purchasedDate_res == '2':
                purchasedDate = input("Enter a different date in YYYY-MM-DD format: ")
                purchasedDate = purchasedDate + self.MARVEL_YYYY_MM_DD_SUFFIX

            # Purchased Price
            for price in marvel_comic_data['prices']:
                if price['type'] == priceType:
                    purchasedPrice = price['price']
                    break
            purchasedPrice_res = input(f"Purchased Price:\n(1) {purchasedPrice}\n(2) Enter different price?\n> ")
            if purchasedPrice_res == '2':
                purchasedPrice = float(input("Enter a purchase price: "))

        else:
            print("INVALID RESPONSE: TRY AGAIN...") if self.LOOKUP_DEBUG else 0
            return self.get_purchased_details(marvel_comic_data)

        return purchasedDate, purchasedPrice, purchasedType

    def _make_comic_book_object_byUPC(self, marvel_comic_data, barcode: str):
        """
        Create a ComicBook() object with the api response data and the barcode
        :param marvel_comic_data: json response from the marvel lookup api
        :param barcode: the barcode key
        """
        purchasedDate, purchasedPrice, purchasedType, isPurchased = None, None, None, False
        isPurchased_res = input("Did you purchase this comic:\n(y/n) > ")
        if isPurchased_res == 'y' or isPurchased_res == 'Y':
            purchasedDate, purchasedPrice, purchasedType = self.get_purchased_details(marvel_comic_data)
            isPurchased = True

        # establish a connection with the ComicBook object Pass database control to the comic book object
        cbObj = ComicBook(self.db, marvel_comic_data, purchasedDate, purchasedPrice, purchasedType, isPurchased)

        # Saves the comic book objects to its member variables
        cbObj.save_properties()

        # save the comic book object in a dictionary with the barcode as the key identifier and the
        # ComicBook() object as the value
        self.comic_books[barcode] = cbObj

        # move the barcode from the queued_barcodes to the lookedUp_barcodes
        self.lookedUp_barcodes[barcode] = {
                'cb'    : self.comic_books[barcode]['cb'],
                'prefix': self.queued_barcodes[barcode]['prefix']
        }

    def upload_complete_comic_book_byUPC(self, barcode: str):
        """
        Create a new database record for the looked up comic book. First uploads any non-existent foreign key
        dependencies and then uploads the entire comic_book object.
        :param barcode: barcode key identifier
        """

        # barcode has not already been lookedUp AND committed to database
        if barcode not in self.committed_barcodes:
            # Create new records for the different member variables that also represent database entities.
            # For example, create a new series if it does not already exist so that the Comics seriesId
            # foreign key dependency can be established.
            self.comic_books[barcode].upload_new_records()

            # Once all the foreign key dependencies have been established, go ahead and create the
            # comic book entity with all of its foreign key dependencies
            self.comic_books[barcode].upload_comic_book()

            # Once the ComicBook() has been uploaded, go ahead and create the comics_has_relationships
            self.comic_books[barcode].upload_comics_has_relationships()

            # move the ComicBook() object from the lookedUp_barcodes to the committed_barcodes
            self.committed_barcodes[barcode] = {
                    'cb'    : self.comic_books[barcode]['cb'],
                    'prefix': self.queued_barcodes[barcode]['prefix']
            }

        else:
            print("BARCODE ALREADY COMMITTED TO DATABASE...") if self.LOOKUP_DEBUG else 0

    def _make_comic_book_object_byID(self, marvel_comic_data, comic_id: int):
        """
        Create a Comic() object with the api response data and the creator_id
        :param marvel_comic_data: json response from the marvel lookup api
        :param comic_id: id of the comic
        """

        # establish a connection with the ComicBook object and pass database control to the ComicBook object
        comicObj = ComicBook(self.db, marvel_comic_data)

        # Saves the ComicBook objects to its member variables
        comicObj.save_properties()

        # link the comicObj to the appropriate comic_id
        self.comic_books[comic_id] = comicObj

    def update_complete_comic_book_byID(self, comic_id: int):
        """
        Update/Create a new database record for the looked up Comic Object. First uploads any non-existent foreign key
        dependencies and then uploads the entire Comic object.
        :param comic_id: comic's identification number
        """

        # Valid creator id
        if comic_id in self.comic_books:
            # Create new records for the different member variables that also represent database entities.
            # For example, create a new series if it does not already exist so that the Creators seriesId
            # foreign key dependency can be established.
            self.comic_books[comic_id].upload_new_records()

            # Once all the foreign key dependencies have been established, go ahead and create the
            # ComicBook entity with all of its foreign key dependencies
            self.comic_books[comic_id].upload_comic_book()

            # Once the Comic() has been uploaded, go ahead and create the comics_has_relationships
            self.comic_books[comic_id].upload_comics_has_relationships()

        else:
            print(f"INVALID COMIC ID {comic_id}...") if self.LOOKUP_DEBUG else 0

    ################################################################
    #  MAKE CREATOR
    ################################################################
    def _make_creator_object(self, marvel_creator_data, creator_id: int):
        """
        Create a Creator() object with the api response data and the creator_id
        :param marvel_creator_data: json response from the marvel lookup api
        :param creator_id: id of the creator
        """

        # establish a connection with the Creator object and pass database control to the Creator object
        creatorObj = Creator(self.db, marvel_creator_data)

        # Saves the creator objects to its member variables
        creatorObj.save_properties()

        # link the creatorObj to the appropriate creator_id
        self.creators[creator_id] = creatorObj

    def update_complete_creator(self, creator_id: int):
        """
        Create a new database record for the looked up Creator Object. First uploads any non-existent foreign key
        dependencies and then uploads the entire Creator object.
        :param creator_id: creator's identification number
        """

        # Valid creator id
        if creator_id in self.creators:
            # Create new records for the different member variables that also represent database entities.
            # For example, create a new series if it does not already exist so that the Creators seriesId
            # foreign key dependency can be established.
            self.creators[creator_id].upload_new_records()

            # Once all the foreign key dependencies have been established, go ahead and create the
            # Creator entity with all of its foreign key dependencies
            self.creators[creator_id].upload_creator()

            # Once the Creator() has been uploaded, go ahead and create the creators_has_relationships
            self.creators[creator_id].upload_creator_has_relationships()

        else:
            print(f"INVALID CREATOR ID {creator_id}...") if self.LOOKUP_DEBUG else 0

    ################################################################
    #  MAKE EVENTS
    ################################################################
    def _make_event_object(self, marvel_event_data, event_id: int):
        """
        Create a Event() object with the api response data and the event_id
        :param marvel_event_data: json response from the marvel lookup api
        :param event_id: id of the event
        """

        # establish a connection with the Event() object and pass database control to the Event() object
        eventObj = Event(self.db, marvel_event_data)

        # Saves the event objects to its member variables
        eventObj.save_properties()

        # link the eventObj to the appropriate event_id
        self.events[event_id] = eventObj

    def update_complete_event(self, event_id: int):
        """
        Create a new database record for the looked up Event() Object. First uploads any non-existent foreign key
        dependencies and then uploads the entire Event object.
        :param event_id: event's identification number
        """

        # Valid event id
        if event_id in self.events:
            # Create new records for the different member variables that also represent database entities.
            # For example, create a new series if it does not already exist so that the Story() storyId
            # foreign key dependency can be established.
            self.events[event_id].upload_new_records()

            # Once all the foreign key dependencies have been established, go ahead and create the
            # Event entity with all of its foreign key dependencies
            self.events[event_id].upload_event()

            # Once the Event() has been uploaded, go ahead and create the entity_has_relationships
            self.events[event_id].upload_event_has_relationships()

        else:
            print(f"INVALID EVENT ID {event_id}...") if self.LOOKUP_DEBUG else 0

    ################################################################
    #  MAKE SERIES
    ################################################################
    def _make_series_object(self, marvel_series_data, series_id: int):
        """
        Create a Series() object with the api response data and the series_id
        :param marvel_series_data: json response from the marvel lookup api
        :param series_id: id of the series
        """

        # establish a connection with the Series() object and pass database control to the Series() object
        seriesObj = Series(self.db, marvel_series_data)

        # Saves the series objects to its member variables
        seriesObj.save_properties()

        # link the seriesObj to the appropriate series_id
        self.series[series_id] = seriesObj

    def update_complete_series(self, series_id: int):
        """
        Create a new database record for the looked up Series() Object. First uploads any non-existent foreign key
        dependencies and then uploads the entire Series object.
        :param series_id: series's identification number
        """

        # Valid creator id
        if series_id in self.series:
            # Create new records for the different member variables that also represent database entities.
            # For example, create a new series if it does not already exist so that the Series() seriesId
            # foreign key dependency can be established.
            self.series[series_id].upload_new_records()

            # Once all the foreign key dependencies have been established, go ahead and create the
            # Series entity with all of its foreign key dependencies
            self.series[series_id].upload_series()

            # Once the Series() has been uploaded, go ahead and create the entity_has_relationships
            self.series[series_id].upload_series_has_relationships()

        else:
            print(f"INVALID SERIES ID {series_id}...") if self.LOOKUP_DEBUG else 0

    ################################################################
    #  MAKE STORIES
    ################################################################
    def _make_story_object(self, marvel_story_data, story_id: int):
        """
        Create a Story() object with the api response data and the story_id
        :param marvel_story_data: json response from the marvel lookup api
        :param story_id: id of the story
        """

        # establish a connection with the Story() object and pass database control to the Story() object
        storyObj = Story(self.db, marvel_story_data)

        # Saves the story objects to its member variables
        storyObj.save_properties()

        # link the storyObj to the appropriate story_id
        self.stories[story_id] = storyObj

    def update_complete_story(self, story_id: int):
        """
        Create a new database record for the looked up Story() Object. First uploads any non-existent foreign key
        dependencies and then uploads the entire Story object.
        :param story_id: story's identification number
        """

        # Valid creator id
        if story_id in self.stories:
            # Create new records for the different member variables that also represent database entities.
            # For example, create a new series if it does not already exist so that the Story() storyId
            # foreign key dependency can be established.
            self.stories[story_id].upload_new_records()

            # Once all the foreign key dependencies have been established, go ahead and create the
            # Story entity with all of its foreign key dependencies
            self.stories[story_id].upload_story()

            # Once the Story() has been uploaded, go ahead and create the entity_has_relationships
            self.stories[story_id].upload_story_has_relationships()

        else:
            print(f"INVALID STORY ID {story_id}...") if self.LOOKUP_DEBUG else 0

    ################################################################
    #  MAKE VARIANT (COMIC)
    ################################################################
    def update_complete_variant(self, variant_id: int):
        """
        Update/Create a new database record for the looked up Comic Object. First uploads any non-existent foreign key
        dependencies and then uploads the entire Comic object.
        :param variant_id: comic's identification number
        """

        # Valid creator id
        if variant_id in self.variants:
            # Create new records for the different member variables that also represent database entities.
            # For example, create a new series if it does not already exist so that the Creators seriesId
            # foreign key dependency can be established.
            self.variants[variant_id].upload_new_records()

            # Once all the foreign key dependencies have been established, go ahead and create the
            # ComicBook entity with all of its foreign key dependencies
            self.variants[variant_id].upload_comic_book()

            # Once the Comic() has been uploaded, go ahead and create the comic_has_relationships
            self.variants[variant_id].upload_comics_has_relationships()

        else:
            print(f"INVALID VARIANT ID {variant_id}...") if self.LOOKUP_DEBUG else 0

    def _make_variant_object(self, marvel_variant_data, variant_id: int):
        """
        Create a Comic() object with the api response data and the creator_id
        :param marvel_variant_data: json response from the marvel lookup api
        :param variant_id: id of the comic
        """

        # establish a connection with the ComicBook object and pass database control to the ComicBook object
        variantObj = Variant(self.db, marvel_variant_data)

        # Saves the ComicBook objects to its member variables
        variantObj.save_properties()

        # link the comicObj to the appropriate comic_id
        self.variants[variant_id] = variantObj

    ####################################################################################################################
    #
    #                                         DATABASE INTERACTIONS
    #
    ####################################################################################################################
    def get_barcodes_from_db(self):
        """
        Queries the database for any queued_barcodes in the scanned_upc_codes table.
        """

        res_data = self.db.get_upcs_from_buffer()

        for upc in res_data:
            upc_prefix = upc['upc_code'][:5]
            upc_code = upc['upc_code'][6:]
            upload_date = upc['date_uploaded']

            if upc_code not in self.queued_barcodes:
                self.queued_barcodes[upc_code] = {'prefix': upc_prefix, 'upload_date': upload_date}

            # Conflicting dates
            elif self.queued_barcodes[upc_code]['upload_date'] != upload_date:
                self.queued_barcodes[upc_code]['upload_date'] = self._reconcile_duplicate_upc(
                        self.queued_barcodes[upc_code]['upload_date'], upload_date
                )

            # duplicate with same date
            else:
                print("Duplicate barcode found but dates not conflicting...") if self.LOOKUP_DEBUG else 0

    def get_stale_entity_from_db(self, entity: str):
        """
        Queries the database for any stale entity. A stale entity is one with a modified date more than a year
        old or no modified date. No modified date is usually a result of uploading a entity to satisfy a foreign key
        dependency for some other entity.
        """
        if entity in self.COMIC_DEPENDENCIES or entity == self.COMIC_ENTITY:
            if entity == self.CHARACTER_ENTITY:
                entity_dict = self.characters
            elif entity == self.COMIC_ENTITY:
                entity_dict = self.comic_books
            elif entity == self.CREATOR_ENTITY:
                entity_dict = self.creators
            elif entity == self.EVENT_ENTITY:
                entity_dict = self.events
            elif entity == self.SERIES_ENTITY:
                entity_dict = self.series
            else:
                entity_dict = self.stories

            res_data = self.db.get_stale_entity(entity)

            for entity_record in res_data:
                entity_id = entity_record['id']
                if entity_id not in entity_dict:
                    entity_dict[entity_id] = None
                # duplicate with same date
                else:
                    print(f"DUPLICATE {entity_record} FOUND...") if self.LOOKUP_DEBUG else 0

    def get_purchased_comic_ids_from_db(self):
        """
        Gets the comic ids of the purchased comics
        """
        res_data = self.db.get_comic_purchased_ids()

        for comic in res_data:
            comic_id = comic['comicId']
            if comic_id not in self.comic_books:
                self.comic_books[comic_id] = None
            # duplicate with same date
            else:
                print("DUPLICATE COMIC FOUND...") if self.LOOKUP_DEBUG else 0

    def get_comic_has_entity_ids_from_db(self, dependency: str, comic_id: int):
        """ Get the given ids of a comic dependent entity """
        if dependency in self.COMIC_DEPENDENCIES:
            if dependency == self.CHARACTER_ENTITY:
                id_name = "characterId"
                entity_dict = self.characters
            elif dependency == self.CREATOR_ENTITY:
                id_name = "creatorId"
                entity_dict = self.creators
            elif dependency == self.EVENT_ENTITY:
                id_name = "eventId"
                entity_dict = self.events
            elif dependency == self.SERIES_ENTITY:
                id_name = "seriesId"
                entity_dict = self.series
            elif dependency == self.VARIANT_ENTITY:
                id_name = "variantId"
                entity_dict = self.variants
            else:
                id_name = "storyId"
                entity_dict = self.stories

            res_data = self.db.get_comic_has_entity_ids(dependency, comic_id)

            for entity in res_data:
                entity_id = entity[id_name]
                if entity_id not in entity_dict:
                    entity_dict[entity_id] = None
                else:
                    print(f"DUPLICATE {entity} FOUND ...") if self.LOOKUP_DEBUG else 0

        else:
            print("NO SUCH COMIC HAS ENTITY...") if self.LOOKUP_DEBUG else 0

    def remove_committed_from_buffer_db(self):
        """
        Deletes the barcodes that have been committed to the database from the scanned_upc_codes table
        """

        for committed_barcode in self.committed_barcodes:
            full_barcode = self.committed_barcodes[committed_barcode]['prefix'] + '-' + committed_barcode
            self.db.delete_from_scanned_upc_codes_table(full_barcode)

        self.committed_barcodes = {}

    ####################################################################################################################
    #
    #                                       GETTERS AND SETTERS
    #
    ####################################################################################################################

    def get_num_queued_barcodes(self) -> int:
        """
        Gets the number of barcodes ready for api lookup.
        These barcodes have not been looked up yet. This is the queuing stage.
        :return: int length of self_barcodes{}
        """
        return len(self.queued_barcodes)

    def get_num_lookedUp_barcodes(self) -> int:
        """
        Gets the number of barcodes that have already been queried and stored as a comic book object.
        These barcodes are waiting to be committed to the comic book database.
        :return: integer number of barcodes that have been looked up and have a comic book object
        """
        return len(self.lookedUp_barcodes)

    def get_num_committed_barcodes(self) -> int:
        """
        Gets the number of barcodes that have already been queried, stored, and committed to the database.
        These barcodes are completely done and can be deleted from the scanned_upc_codes database.
        :return: integer number of barcodes that have been committed to the comic_books database
        """
        return len(self.committed_barcodes)

    def print_queued_barcodes(self):
        """
        Prints the formatted list of barcodes in the queued_barcodes dictionary
        """
        i = 1
        for queued_barcode in self.queued_barcodes:
            print(f"({i})\t{queued_barcode}")
            i += 1

    def print_lookedUp_barcodes(self):
        """
        Prints the formatted list of barcodes in the lookedUp_barcodes dictionary
        """
        i = 1
        for lookedup_barcode in self.lookedUp_barcodes:
            print(f"({i})\t{lookedup_barcode}")
            i += 1

    def print_committed_barcodes(self):
        """
        Print the barcodes committed to the database
        """
        i = 1
        for committed_barcode in self.committed_barcodes:
            print(f"({i})\t{committed_barcode}")
            i += 1

    def get_num_entity(self, entity_name: str) -> int:
        """
        Gets the number of stale Entities.
        :return: integer number of stale entities.
        """
        if entity_name in self.ENTITIES:
            if entity_name == self.CHARACTER_ENTITY:
                return len(self.characters)
            if entity_name == self.CREATOR_ENTITY:
                return len(self.creators)
            if entity_name == self.EVENT_ENTITY:
                return len(self.events)
            if entity_name == self.SERIES_ENTITY:
                return len(self.series)
            if entity_name == self.STORY_ENTITY:
                return len(self.stories)
            if entity_name == self.COMIC_ENTITY:
                return len(self.comic_books)
            if entity_name == self.VARIANT_ENTITY:
                return len(self.variants)

        print(f"ENTITY: {entity_name} DOES NOT EXIST") if self.LOOKUP_DEBUG else 0
        return 0

    def print_entity_ids(self, entity_name: str):
        """
        Print a list of the entity ids
        :param entity_name: the name of the entity list to print
        """
        i = 1
        entity_dict = {}
        if entity_name in self.ENTITIES:
            if entity_name == self.CHARACTER_ENTITY:
                entity_dict = self.characters
            if entity_name == self.CREATOR_ENTITY:
                entity_dict = self.creators
            if entity_name == self.EVENT_ENTITY:
                entity_dict = self.events
            if entity_name == self.SERIES_ENTITY:
                entity_dict = self.series
            if entity_name == self.STORY_ENTITY:
                entity_dict = self.stories
            if entity_name == self.COMIC_ENTITY:
                entity_dict = self.comic_books
            if entity_name == self.VARIANT_ENTITY:
                entity_dict = self.variants

            for entity in entity_dict:
                print(f"({i})\t{entity}")
                i += 1
        else:
            print(f"ENTITY: {entity_name} DOES NOT EXIST") if self.LOOKUP_DEBUG else 0

    ####################################################################################################################
    #
    #                                               UTILITIES
    #
    ####################################################################################################################

    @staticmethod
    def _get_marvel_api_hash():
        """
        Generates a md5 hash of timestamp + private key + public key
        :return: returns the hash digest and integer time stamp
        """

        timestamp = int(time.time())
        input_string = str(
                str(timestamp)
                + keys.private_keys.marvel_developer_priv_key
                + keys.pub_keys.marvel_developer_pub_key
        )

        return hashlib.md5(input_string.encode("utf-8")).hexdigest(), timestamp

    def _reconcile_duplicate_upc(self, og_date, conflict_date):
        """
        Reconciles duplicate queued_barcodes with conflicting dates
        :param og_date: date from barcode previously scanned
        :param conflict_date: date of the current (newer) barcode
        :return: the user preferred date
        """

        print(
                f"Duplicate found with conflicting date. Which one do you want to keep:"
                f"\n\t(1) {og_date}"
                f"\n\t(2) {conflict_date}"
        )
        keep_res = input(">>> ")

        # keep the original date
        if keep_res[0] == '1':
            return og_date
        # keep the current date for barcode otherwise keep the original date for barcode
        elif keep_res[0] == '2':
            return conflict_date
        # invalid entry. try again
        else:
            print("Invalid entry...")
            return self._reconcile_duplicate_upc(og_date, conflict_date)

    def quit_program(self):
        """
        Exits the LookUp Program
        """

        if self.get_num_queued_barcodes() > 0:
            quit_res = input("YOU STILL HAVE BARCODES IN THE QUEUE...ARE YOU SURE YOU WANT TO QUIT (y/n)?: ") \
                if self.LOOKUP_DEBUG else 0

            if quit_res == 'y' or quit_res == 'Y':
                print("Cleaning up committed barcodes...") if self.LOOKUP_DEBUG else 0
                self.remove_committed_from_buffer_db()
                print("QUITTING LOOKUP PROGRAM...") if self.LOOKUP_DEBUG else 0
                exit(1)
            else:
                return

        else:
            print("Cleanining up committed barcodes...") if self.LOOKUP_DEBUG else 0
            self.remove_committed_from_buffer_db()
            print("QUITTING LOOKUP PROGRAM...") if self.LOOKUP_DEBUG else 0
            exit(1)
