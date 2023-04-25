"""
Author: Zane Miller
Email: millerzanem@gmail.com
Date: 04/16/2023
Description: Driver class for looking up scanned_barcodes
"""
import hashlib
import time

import requests

import keys.private_keys
import keys.pub_keys
from backend.models.ComicBook import ComicBook
from backend.models.Creators import Creator
from backend.models.Series import Series
from backend.models.Stories import Story

COMICS_URL = "https://gateway.marvel.com/v1/public/comics"
CHARACTERS_URL = "https://gateway.marvel.com/v1/public/characters"
CREATORS_URL = "https://gateway.marvel.com/v1/public/creators"
EVENTS_URL = "https://gateway.marvel.com/v1/public/events"
SERIES_URL = "https://gateway.marvel.com/v1/public/series"
STORIES_URL = "https://gateway.marvel.com/v1/public/stories"
MARVEL_YYYY_MM_DD_SUFFIX = "T00:00:00-0400"


class Lookup:
    """ Lookup object responsible for looking up queued_barcodes in scanned upc buffer """

    def __init__(self, lookup_db):
        """
        Object represents a lookup object with a dictionary of barcodes, comic books and a db connection
        """
        self.queued_barcodes = {}  # (queued_barcodes[barcode] = {prefix: barcode_prefix, upload_date: ''})
        self.lookedUp_barcodes = {}  # (lookedUp_barcodes[barcode] = {cb: comic_books[barcode], prefix: ''})
        self.committed_barcodes = {}  # (committed_barcodes[barcode] = {cb: comic_books[barcode], prefix: ''})

        self.comic_books = {}  # (comic_books[barcode] = {cb: ComicBook(), prefix: ''})
        self.creators = {}  # (creators[creatorId] = Creator())
        self.series = {}  # (series[seriesId] = Series())
        self.stories = {}  # (stories[storyId] = Story())

        self.db = lookup_db
        self.LOOKUP_DEBUG = True

    ####################################################################################################################
    #
    #                                           HTTPS INTERACTIONS
    #
    ####################################################################################################################
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
            request = requests.get(COMICS_URL, PARAMS)
            self.marvel_comic_data = request.json()

            if self.marvel_comic_data['data']['count'] == 0:
                print(f"No comics found with {barcode} upc") if self.LOOKUP_DEBUG else 0
            elif self.marvel_comic_data['data']['count'] > 1:
                print("TOO MANY COMIC BOOKS FOUND...") if self.LOOKUP_DEBUG else 0
            else:
                self._make_comic_book_object(barcode)
        else:
            print("BARCODE HAS ALREADY BEEN LOOKED UP...WAITING TO BE COMMITTED") if self.LOOKUP_DEBUG else 0

    def lookup_marvel_creator_by_id(self, creator_id: int):
        """
        Pulls creator information from CREATORS_URL + '/{creatorId}'
        :param creator_id: the integer id of the creator resource
        """

        if creator_id in self.creators:
            hash_str, timestamp = self._get_marvel_api_hash()

            PARAMS = {'apikey': keys.pub_keys.marvel_developer_pub_key, 'ts': timestamp, 'hash': hash_str}
            endpoint = CREATORS_URL + '/' + str(creator_id)

            request = requests.get(endpoint, PARAMS)
            data = request.json()

            if data['data']['count'] == 0:
                print(f"No Creator found with {creator_id} creator id") if self.LOOKUP_DEBUG else 0
            elif data['data']['count'] > 1:
                print("TOO MANY CREATORS FOUND...") if self.LOOKUP_DEBUG else 0
            else:
                self._make_creator_object(data['data']['results'][0], creator_id)

    def lookup_marvel_series_by_id(self, series_id: int):
        """
        Pulls series information from SERIES_URL + '/{seriesId}'
        :param series_id: the integer id of the series resource
        """

        if series_id in self.series:
            hash_str, timestamp = self._get_marvel_api_hash()

            PARAMS = {'apikey': keys.pub_keys.marvel_developer_pub_key, 'ts': timestamp, 'hash': hash_str}
            endpoint = SERIES_URL + '/' + str(series_id)

            request = requests.get(endpoint, PARAMS)
            data = request.json()

            if data['data']['count'] == 0:
                print(f"No Series found with {series_id} series id") if self.LOOKUP_DEBUG else 0
            elif data['data']['count'] > 1:
                print("TOO MANY SERIES FOUND...") if self.LOOKUP_DEBUG else 0
            else:
                self._make_series_object(data['data']['results'][0], series_id)

    def lookup_marvel_story_by_id(self, story_id: int):
        """
        Pulls story information from STORIES_URL + '/{storyId}'
        :param story_id: the integer id of the story resource
        """

        if story_id in self.stories:
            hash_str, timestamp = self._get_marvel_api_hash()

            PARAMS = {'apikey': keys.pub_keys.marvel_developer_pub_key, 'ts': timestamp, 'hash': hash_str}
            endpoint = STORIES_URL + '/' + str(story_id)

            request = requests.get(endpoint, PARAMS)
            data = request.json()

            if data['data']['count'] == 0:
                print(f"No Stories found with {story_id} story id") if self.LOOKUP_DEBUG else 0
            elif data['data']['count'] > 1:
                print("TOO MANY STORIES FOUND...") if self.LOOKUP_DEBUG else 0
            else:
                self._make_story_object(data['data']['results'][0], story_id)

    ####################################################################################################################
    #
    #                                       OBJECT INTERACTIONS
    #
    ####################################################################################################################

    ################################################################
    #  MAKE COMIC
    ################################################################

    def get_purchased_details(self) -> tuple[str, float, str]:
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
            for date in self.marvel_comic_data['data']['results']['dates']:
                if date['type'] == dateType:
                    purchasedDate = date['date']
                    break
            purchasedDate_res = input(f"Purchased Date:\n(1) {purchasedDate}\n(2) Enter different date?\n> ")
            if purchasedDate_res == '2':
                purchasedDate = input("Enter a different date in YYYY-MM-DD format: ")
                purchasedDate = purchasedDate + MARVEL_YYYY_MM_DD_SUFFIX

            # Purchased Price
            for price in self.marvel_comic_data['data']['results']['prices']:
                if price['type'] == priceType:
                    purchasedPrice = price['price']
                    break
            purchasedPrice_res = input(f"Purchased Price:\n(1) {purchasedPrice}\n(2) Enter different price?\n> ")
            if purchasedPrice_res == '2':
                purchasedPrice = float(input("Enter a purchase price: "))

        else:
            print("INVALID RESPONSE: TRY AGAIN...") if self.LOOKUP_DEBUG else 0
            return self.get_purchased_details()

        return purchasedDate, purchasedPrice, purchasedType

    def _make_comic_book_object(self, barcode):
        """
        Create a ComicBook() object with the api response data and the barcode
        :param barcode: the barcode key
        """
        purchasedDate, purchasedPrice, purchasedType, isPurchased = None, None, None, False
        isPurchased_res = input("Did you purchase this comic:\n(y/n) > ")
        if isPurchased_res == 'y' or isPurchased_res == 'Y':
            purchasedDate, purchasedPrice, purchasedType = self.get_purchased_details()
            isPurchased = True

        # establish a connection with the ComicBook object Pass database control to the comic book object
        cb = ComicBook(self.db, self.marvel_comic_data, purchasedDate, purchasedPrice, purchasedType, isPurchased)

        # Saves the comic book objects to its member variables
        cb.save_properties()

        # save the comic book object in a dictionary with the barcode as the key identifier and the
        # ComicBook() object as the value
        self.comic_books[barcode] = {
                'cb'    : cb,
                'prefix': self.queued_barcodes[barcode]['prefix']
        }

        # move the barcode from the queued_barcodes to the lookedUp_barcodes
        self.lookedUp_barcodes[barcode] = {
                'cb'    : self.comic_books[barcode]['cb'],
                'prefix': self.comic_books[barcode]['prefix']
        }

    def upload_comic_book(self, barcode: str):
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
            self.comic_books[barcode]['cb'].upload_new_records()

            # Once all the foreign key dependencies have been established, go ahead and create the
            # comic book entity with all of its foreign key dependencies
            self.comic_books[barcode]['cb'].upload_comic_book()

            # Once the ComicBook() has been uploaded, go ahead and create the comics_has_relationships
            self.comic_books[barcode]['cb'].upload_comics_has_relationships()

            # move the ComicBook() object from the lookedUp_barcodes to the committed_barcodes
            self.committed_barcodes[barcode] = {
                    'cb'    : self.comic_books[barcode]['cb'],
                    'prefix': self.comic_books[barcode]['prefix']
            }

        else:
            print("BARCODE ALREADY COMMITTED TO DATABASE...") if self.LOOKUP_DEBUG else 0

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
    #  MAKE SERIES
    ################################################################
    def _make_series_object(self, marvel_series_data, series_id):
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
    def _make_story_object(self, marvel_story_data, story_id):
        """
        Create a Story() object with the api response data and the story_id
        :param marvel_story_data: json response from the marvel lookup api
        :param story_id: id of the story
        """

        # establish a connection with the Series() object and pass database control to the Series() object
        storyObj = Story(self.db, marvel_story_data)

        # Saves the series objects to its member variables
        storyObj.save_properties()

        # link the seriesObj to the appropriate series_id
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

    def get_stale_creators_from_db(self):
        """
        Queries the database for any stale creators. A stale creator is one with a modified date more than a year
        old or no modified date. No modified date is usually a result of uploading a creator to satisfy a foreign key
        dependency for some other entity.
        """

        res_data = self.db.get_stale_creators()

        for creator in res_data:
            creator_id = creator['id']
            if creator_id not in self.creators:
                self.creators[creator_id] = None
            # duplicate with same date
            else:
                print("DUPLICATE CREATOR FOUND...") if self.LOOKUP_DEBUG else 0

    def get_stale_series_from_db(self):
        """
        Queries the database for any stale series. A stale series is one with a modified date more than a year
        old or no modified date. No modified date is usually a result of uploading a series to satisfy a foreign key
        dependency for some other entity.
        """

        res_data = self.db.get_stale_series()

        for series in res_data:
            series_id = series['id']
            if series_id not in self.series:
                self.series[series_id] = None
            # duplicate with same date
            else:
                print("DUPLICATE SERIES FOUND...") if self.LOOKUP_DEBUG else 0

    def get_stale_stories_from_db(self):
        """
        Queries the database for any stale stories. A stale stories is one with a modified date more than a year
        old or no modified date. No modified date is usually a result of uploading a stories to satisfy a foreign key
        dependency for some other entity.
        """

        res_data = self.db.get_stale_stories()

        for story in res_data:
            story_id = story['id']
            if story_id not in self.stories:
                self.stories[story_id] = None
            # duplicate with same date
            else:
                print("DUPLICATE STORY FOUND...") if self.LOOKUP_DEBUG else 0

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

    def get_num_stale_creators(self) -> int:
        """
        Gets the number of stale creators.
        :return: integer number of stale creators.
        """
        return len(self.creators)

    def get_num_stale_series(self) -> int:
        """
        Gets the number of stale series.
        :return: integer number of stale series.
        """
        return len(self.series)

    def get_num_stale_stories(self) -> int:
        """
        Gets the number of stale stories.
        :return: integer number of stale stories.
        """
        return len(self.stories)

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
        Prints the formatted list of barcodes in the committed_barcodes dictionary
        """
        i = 1
        for committed_barcode in self.committed_barcodes:
            print(f"({i})\t{committed_barcode}")
            i += 1

    def print_creator_ids(self):
        i = 1
        for creator in self.creators:
            print(f"({i})\t{creator}")
            i += 1

    def print_series_ids(self):
        i = 1
        for series in self.series:
            print(f"({i})\t{series}")
            i += 1

    def print_story_ids(self):
        i = 1
        for story in self.stories:
            print(f"({i})\t{story}")
            i += 1

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
