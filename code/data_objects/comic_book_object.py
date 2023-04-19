"""
Author: Zane Miller
Email: millerzanem@gmail.com
Date: 04/17/2023
Description: Class drivers for looking up marvel comics with marvel public api
"""
import datetime
import hashlib
import json
import time

import requests as requests

from code.classes.lookup_driver import COMICS_URL
from code.database.db_driver import DB
from keys.private_keys import marvel_developer_priv_key
from keys.pub_keys import marvel_developer_pub_key

CHARACTERS_TABLE_NAME = 'Characters'
COMICS_TABLE_NAME = 'Comics'
CREATORS_TABLE_NAME = 'Creators'
EVENTS_TABLE_NAME = 'Events'
IMAGES_TABLE_NAME = 'Images'
SERIES_TABLE_NAME = 'Series'
STORIES_TABLE_NAME = 'Stories'
URLS_TABLE_NAME = 'URLs'
PURCHASED_COMICS_TABLE_NAME = 'PurchasedComics'
COMICS_HAS_CHARACTERS_TABLE_NAME = 'Comics_has_Characters'
COMICS_HAS_CREATORS_TABLE_NAME = 'Comics_has_Creators'
COMICS_HAS_EVENTS_TABLE_NAME = 'Comics_has_Events'
COMICS_HAS_IMAGES_TABLE_NAME = 'Comics_has_Images'
COMICS_HAS_STORIES_TABLE_NAME = 'Comics_has_Stories'
COMICS_HAS_URLS_TABLE_NAME = 'Comics_has_URLs'


class ComicBook:
    """
    Comic Book object responsible for looking up comic book details by
    ID from the marvel API and uploading data to database
    """

    def __init__(self, db_connection):
        """ Represents a Comic book based on the marvel comic developer api json response model """
        self.db = db_connection
        self.data = None
        self.count = None  # int, optional

        self.id = None  # int, optional
        self.digitalId = None  # int, optional
        self.title = None  # string, optional
        self.issueNumber = None  # double, optional
        self.variantDescription = None  # string, optional
        self.description = None  # string, optional
        self.modified = None  # Date, optional
        self.isbn = None  # string, optional
        self.upc = None  # string, optional
        self.diamondCode = None  # string, optional
        self.ean = None  # string, optional
        self.issn = None  # string, optional
        self.format = None  # string, optional
        self.pageCount = None  # int, optional
        self.textObjects = {}  # Array[TextObject], optional
        # self.textObjects[type] = {
        #     'language': string, optional,
        #     'text': string, optional
        # }
        self.resourceURI = None  # string, optional
        self.urls = set()  # set of tuples (type, url)
        self.seriesDetail = {}  # (seriesDetail[series_id] = {title: '', uri: ''})
        self.seriesId = None
        self.variantDetail = {}  # (variantDetail[variant_id] = {title: '', uri: ''})
        self.variantIds = set()  # {variant_ids} ...comics_has...
        self.onsaleDate = None
        self.focDate = None
        self.unlimitedDate = None
        self.digitalPurchaseDate = None
        self.printPrice = None
        self.digitalPurchasePrice = None
        self.thumbnail = None

        self.image_paths = set()  # {image_paths} ... includes thumbnail path as well ...comics_has...
        self.creatorIds = {}  # (creatorIds[creator_id] = [roles]}) ...comics_has...
        self.characterIds = set()  # {character_ids} ...comics_has...
        self.storyIds = set()  # {story_ids} ...comics_has...
        self.eventIds = set()  # {event_ids} ...comics_has...

        self.creatorDetail = {}  # (creatorDetail[creator_id] = {f_name: '', m_name: '', l_name: '', uri: ''})
        self.characterDetail = {}  # (characterDetail[character_id] = {name: '', uri: ''})
        self.storyDetail = {}  # (storyDetail[story_id] = {title: '', type: '', uri: ''})
        self.eventDetail = {}  # (eventDetail[event_id] = {title: '', uri: ''})

        self.originalIssueId = None

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

    def save_properties(self):
        """
        Maps the json response to member class variables
        """
        if self.data:
            self._save_id()
            self._save_digitalId()
            self._save_title()
            self._save_issueNumber()
            self._save_variantDescription()
            self._save_description()
            self._save_modified()
            self._save_isbn()
            self._save_upc()
            self._save_diamondCode()
            self._save_ean()
            self._save_issn()
            self._save_format()
            self._save_pageCount()
            self._save_textObjects()
            self._save_resourceURI()
            self._save_urls()
            self._save_series()
            self._save_variants()
            self._save_dates()
            self._save_prices()
            self._save_images()
            self._save_creators()
            self._save_characters()
            self._save_stories()
            self._save_events()

    def upload_new_records(self):
        """
        Uploads new records to the database before uploading the entire comic book with relevant foreign keys
        """

        self._add_new_url()
        self._add_new_series()
        self._add_new_variant()
        self._add_new_image()
        self._add_new_creator()
        self._add_new_character()
        self._add_new_story()
        self._add_new_event()

    def upload_comic_book(self):
        """
        Compiles the comic_book entities into params tuple to pass to database function for uploading complete comic
        book
        """
        comic_detailURL = None
        comic_purchaseURL = None
        comic_readerURL = None
        comic_inAppLinkURL = None
        for url_type, url_str in self.urls:
            if url_type == 'detail':
                comic_detailURL = url_str
            elif url_type == 'purchase':
                comic_purchaseURL = url_str
            elif url_type == 'reader':
                comic_readerURL = url_str
            elif url_type == 'inAppLink':
                comic_inAppLinkURL = url_str

        params = (self.id, self.digitalId, self.title, self.issueNumber, self.variantDescription, self.description,
                  self.modified, self.isbn, self.upc, self.diamondCode, self.ean, self.issn, self.format,
                  self.pageCount, json.dumps(self.textObjects), self.resourceURI, comic_detailURL, comic_purchaseURL,
                  comic_readerURL, comic_inAppLinkURL, self.onsaleDate, self.focDate, self.unlimitedDate,
                  self.digitalPurchaseDate, self.printPrice, self.digitalPurchasePrice, self.seriesId, self.thumbnail,
                  self.originalIssueId)

        self.db.upload_new_comic_book(params)

    #################################################################
    #          ADD NEW JSON RESPONSE DATA TO CLASS VARIABLES
    #################################################################

    def _save_characters(self):
        """
        A resource list containing the characters which appear in this comic.
        """
        if self.data['characters']['available'] > 0:
            for character in self.data['characters']['items']:
                character_resource_uri = character['resourceURI']
                character_name = character['name']
                character_id = self.get_id_from_resourceURI(character_resource_uri)

                if character_id != -1:
                    # Save to dict for creating new character record
                    if character_id not in self.characterDetail:
                        self.characterDetail[character_id] = {
                            'name': character_name,
                            'uri': character_resource_uri
                        }

                    # characterIds will later be used to create Comics_has_Characters entity
                    if character_id not in self.characterIds:
                        self.characterIds.add(character_id)

    def _save_creators(self):
        """
        A resource list containing the creators associated with this comic.
        """
        if self.data['creators']['available'] > 0:
            for creator in self.data['creators']['items']:
                creator_resource_uri = creator['resourceURI']
                creator_name = creator['name']
                creator_role = creator['role']
                creator_id = self.get_id_from_resourceURI(creator_resource_uri)
                creator_first_name, creator_middle_name, creator_last_name = self.get_split_name(creator_name)

                if creator_id != -1:

                    # save it to the detail dictionary for creating new db record
                    if creator_id not in self.creatorDetail:
                        self.creatorDetail[creator_id] = {
                            'first_name': creator_first_name,
                            'middle_name': creator_middle_name,
                            'last_name': creator_last_name,
                            'uri': creator_resource_uri
                        }

                    # save to creatorIds dictionary with role for Comics_has_Creators entity
                    if creator_id not in self.creatorIds:
                        self.creatorIds[creator_id] = [creator_role]
                    else:
                        self.creatorIds[creator_id].append(creator_role)

    def _save_dates(self):
        """
        A list of key dates for this comic.
        """
        for date in self.data['dates']:
            if date['type'] == "onsaleDate":
                self.onsaleDate = datetime.datetime.strptime(date['date'], "%Y-%m-%dT%H:%M:%S%z")
            elif date['type'] == "focDate":
                self.focDate = datetime.datetime.strptime(date['date'], "%Y-%m-%dT%H:%M:%S%z")
            elif date['type'] == "unlimitedDate":
                self.unlimitedDate = datetime.datetime.strptime(date['date'], "%Y-%m-%dT%H:%M:%S%z")
            elif date['type'] == "digitalPurchaseDate":
                self.digitalPurchaseDate = datetime.datetime.strptime(date['date'], "%Y-%m-%dT%H:%M:%S%z")
            else:
                print(f"{date['type']} DATE TYPE NOT CATEGORIZED")

    def _save_description(self):
        """
        The preferred description of the comic.
        """
        self.description = str(self.data['description'])

    def _save_diamondCode(self):
        """
        The Diamond Code for the comic.
        """
        self.diamondCode = str(self.data['diamondCode'])

    def _save_digitalId(self):
        """
        The ID of the digital comic representation of this comic.
        Will be 0 if the comic is not available digitally.
        """
        self.digitalId = int(self.data['digitalId'])

    def _save_ean(self):
        """
        The EAN barcode for the comic.
        """
        self.ean = str(self.data['ean'])

    def _save_events(self):
        """
        A resource list containing the events in which this comic appears.
        """

        if self.data['events']['available'] > 0:
            for event in self.data['events']['items']:
                event_resource_uri = event['resourceURI']
                event_title = event['name']
                event_id = self.get_id_from_resourceURI(event_resource_uri)

                if event_id != -1:
                    if event_id not in self.eventDetail:
                        self.eventDetail[event_id] = {
                            'title': event_title,
                            'uri': event_resource_uri
                        }

                    if event_id not in self.eventIds:
                        self.eventIds.add(event_id)

    def _save_format(self):
        """
        The publication format of the comic e.g. comic, hardcover, trade paperback.
        """
        self.format = str(self.data['format'])

    def _save_id(self):
        """
        The unique ID of the comic resource.
        """
        self.id = int(self.data['id'])

    def _save_images(self):
        """
        A list of promotional image_paths associated with this comic.
        """

        self._save_thumbnail()

        for image in self.data['image_paths']:
            image_path = image['path']
            image_extension = image['extension']
            full_path = image_path + '.' + image_extension
            if full_path not in self.image_paths:
                self.image_paths.add(full_path)

    def _save_isbn(self):
        """
        The ISBN for the comic (generally only populated for collection formats).
        """
        self.isbn = str(self.data['isbn'])

    def _save_issn(self):
        """
        The ISSN barcode for the comic.
        """
        self.issn = str(self.data['issn'])

    def _save_issueNumber(self):
        """
        The number of the issue in the series (will generally be 0 for collection formats).
        """
        self.issueNumber = float(self.data['issueNumber'])

    def _save_modified(self):
        """
        The date the resource was most recently modified.
        """
        self.modified = str(self.data['modified'])

    def _save_pageCount(self):
        """
        The number of story pages in the comic.
        """
        self.pageCount = int(self.data['pageCount'])

    def _save_prices(self):
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

    def _save_resourceURI(self):
        """
        The canonical URL identifier for this resource.
        """
        self.resourceURI = str(self.data['resourceURI'])

    def _save_series(self):
        """
        A summary representation of the series to which this comic belongs.
        """

        if self.data['series']:
            series_uri = self.data['series']['resourceURI']
            series_title = self.data['series']['name']
            series_id = self.get_id_from_resourceURI(series_uri)

            if series_id != -1:
                if series_id not in self.seriesDetail:
                    self.seriesDetail[series_id] = {'title': series_title, 'uri': series_uri}

            self.seriesId = series_id

    def _save_stories(self):
        """
        A resource list containing the stories which appear in this comic.
        """

        if self.data['stories']['available'] > 0:
            for story in self.data['stories']['items']:
                story_resource_uri = story['resourceURI']
                story_title = story['name']
                story_type = story['type']
                story_id = self.get_id_from_resourceURI(story_resource_uri)

                if story_id != -1:
                    # used for creating new db story record
                    if story_id not in self.storyDetail:
                        self.storyDetail[story_id] = {
                            'title': story_title,
                            'type': story_type,
                            'uri': story_resource_uri,
                            'originalIssue': self.id
                        }
                    if story_id not in self.storyIds:
                        self.storyIds.add(story_id)

    def _save_textObjects(self):
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

    def _save_thumbnail(self):
        """
        The representative image for this comic.
        """
        thumbnail_path = self.data['thumbnail']['path']
        thumbnail_extension = self.data['thumbnail']['extension']

        self.thumbnail = str(thumbnail_path + '.' + thumbnail_extension)

        if self.thumbnail not in self.image_paths:
            self.image_paths.add(self.thumbnail)

    def _save_title(self):
        """
        The canonical title of the comic.
        """
        self.title = str(self.data['title'])

    def _save_upc(self):
        """
        The UPC barcode number for the comic (generally only populated for periodical formats).
        """
        self.upc = str(self.data['upc'])

    def _save_urls(self):
        """
        A set of public web-site URLs for the resource.
        """
        for url in self.data['urls']:
            self.urls.add((url['type'], url['url']))

    def _save_variantDescription(self):
        """
        If the issue is a variant (e.g. an alternate cover, second printing, or director’s cut),
        a text description of the variant.
        """
        self.variantDescription = str(self.data['variantDescription'])

    def _save_variants(self):
        """
        A list of variant issues for this comic
        (includes the "original" issue if the current issue is a variant).
        """

        for variant in self.data['variants']:
            variant_uri = variant['resourceURI']
            variant_title = variant['name']
            variant_id = self.get_id_from_resourceURI(variant_uri)

            if variant_id != -1:
                # used for creating new comic book record for variant
                if variant_id not in self.variantDetail and variant_id != self.id:
                    self.variantDetail[variant_id] = {'title': variant_title, 'uri': variant_uri}

                # used for creating comic_has_variants entity later
                if variant_id not in self.variantIds and variant_id != self.id:
                    self.variantIds.add(variant_id)

    #################################################################
    #               ADD NEW RECORDS TO DATABASE
    #################################################################

    def _add_new_character(self):
        """
        Adds new character to comic_books.characters table if record does not exist
        """

        for character in self.characterIds:
            character_id = character
            character_name = self.characterDetail[character_id]['name']
            character_resource_uri = self.characterDetail[character_id]['uri']

            self.db.upload_new_character_record(character_id, character_name, character_resource_uri)

    def _add_new_creator(self):
        """
        Adds new creator records to comic_books.creators with resourceURI, id, and first, middle and last names
        """
        for creator in self.creatorDetail:
            creator_id = creator
            f_name = self.creatorDetail[creator_id]['first_name']
            m_name = self.creatorDetail[creator_id]['middle_name']
            l_name = self.creatorDetail[creator_id]['last_name']
            resource_uri = self.creatorDetail[creator_id]['uri']

            self.db.upload_new_creator_record(creator_id, f_name, m_name, l_name, resource_uri)

    def _add_new_event(self):
        """
        Adds a new event to the comic_books.events table if event record does not already exist
        """
        for event in self.eventDetail:
            event_id = event
            event_title = self.eventDetail[event_id]['title']
            event_uri = self.eventDetail[event_id]['uri']

            self.db.upload_new_record_by_table(EVENTS_TABLE_NAME, event_id, event_title, event_uri)

    def _add_new_image(self):
        """
        Adds any image urls to the database that are not currently in the comic_books.Images table
        """

        for image in self.image_paths:
            self.db.upload_new_image_record(image)

    def _add_new_series(self):
        """
        Adds the series to the comic_books.series table if series record does not already exist.
        """

        series_id = self.seriesId
        series_title = self.seriesDetail['title']
        series_uri = self.seriesDetail['uri']

        self.db.upload_new_record_by_table(SERIES_TABLE_NAME, series_id, series_title, series_uri)

    def _add_new_story(self):
        """
        Creates and commits any new story records to comic_books.stories table
        """

        for story in self.storyDetail:
            story_id = story
            story_title = self.storyDetail[story_id]['title']
            story_type = self.storyDetail[story_id]['type']
            story_resource_uri = self.storyDetail[story_id]['uri']
            original_issue = self.storyDetail[story_id]['originalIssue']

            self.db.upload_new_story_record(story_id, story_title, story_resource_uri, story_type, original_issue)

    def _add_new_url(self):
        """
        Adds any new urls without an existing record to the comic_books.URLs table
        """
        for url_type, url_path in self.urls:
            self.db.upload_new_url_record(url_type, url_path)

    def _add_new_variant(self):
        """
        Uploads any variant comic records that do not already exist in the comic_books.comics table
        """

        for variant in self.variantDetail:
            variant_id = variant
            variant_title = variant[variant_id]['title']
            variant_uri = variant[variant_id]['uri']

            self.db.upload_new_record_by_table(COMICS_TABLE_NAME, variant_id, variant_title, variant_uri)

    #################################################################
    #               Comics_has_Relationships
    #################################################################

    def _comics_has_characters(self):
        """
        Upload new record in Comics_has_Characters table
        """
        for characterId in self.characterIds:
            self.db.upload_new_comics_has_characters_record(int(self.id), int(characterId))

    def _comics_has_creators(self):
        """
        Upload new record in Comics_has_Creators table
        """
        for creator in self.creatorIds:
            creator_id = creator
            for role in self.creatorIds[creator_id]:
                self.db.upload_new_comics_has_creators_record(int(self.id), int(creator_id), str(role))

    def _comics_has_events(self):
        """
        Upload new record in Comics_has_Events table
        """
        for event in self.eventIds:
            self.db.upload_new_comics_has_events_record(int(self.id), int(event))

    def _comics_has_images(self):
        """
        Upload new record in Comics_has_Events table
        """
        for image_path in self.image_paths:
            self.db.upload_new_comics_has_images_record(int(self.id), str(image_path))

    def _comics_has_stories(self):
        """
        Upload new record in Comics_has_Events table
        """
        for story in self.storyIds:
            self.db.upload_new_comics_has_stories_record(int(self.id), int(story))

    def _comics_has_urls(self):
        """
        Upload new record in Comics_has_Events table
        """
        for url_type, url_str in self.urls:
            self.db.upload_new_comics_has_urls_record(self.id, url_str)

    def _comics_has_variants(self):
        """
        Upload new record in Comics_has_Events table
        """

        for variant in self.variantIds:
            pass

    #################################################################
    #                       UTILITIES
    #################################################################
    @staticmethod
    def get_split_name(full_name: str) -> tuple[str, str, str]:
        """
        Takes a full name and splits it into first, middle, and last
        :param full_name: full name as a string
        :return: tuple of names (first, middle, last)
        """

        split_name = full_name.split()
        total_names = len(split_name)

        if total_names >= 3:
            first_name = split_name[0]
            last_name = split_name[-1]
            middle_name = "".join(split_name[1:total_names - 1])

        elif total_names == 2:
            first_name = split_name[0]
            middle_name = ""
            last_name = split_name[-1]

        elif total_names == 1:
            first_name = split_name[0]
            middle_name = ""
            last_name = ""
        else:
            first_name = ""
            middle_name = ""
            last_name = ""

        return first_name, middle_name, last_name

    @staticmethod
    def get_id_from_resourceURI(resource_uri: str) -> int:
        """
        Gets the resource id from a resource URI and returns it as an integer
        :param resource_uri: full URI path of the resource
        :return: int of resource id, or -1 if resource id not in expected location
        """

        split_arr = resource_uri.split('/')

        if split_arr[-1].isnumeric():
            return int(split_arr[-1])

        # last index not what we expect
        print(f'CANT FIND RESOURCE ID FROM {resource_uri} split into {split_arr}...')
        return -1


if __name__ == '__main__':
    db = DB()
    db.close_db()
    db = DB()
    cb = ComicBook(db)
