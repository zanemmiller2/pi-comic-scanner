import datetime
import hashlib
import time

from MySQLdb.times import Date

import keys.private_keys
import keys.pub_keys


class Entity:
    """ Generic entity model for inheritance """
    CHARACTERS_TABLE_NAME = 'Characters'
    COMICS_TABLE_NAME = 'Comics'
    CREATORS_TABLE_NAME = 'Creators'
    EVENTS_TABLE_NAME = 'Events'
    IMAGES_TABLE_NAME = 'Images'
    SERIES_TABLE_NAME = 'Series'
    STORIES_TABLE_NAME = 'Stories'
    URLS_TABLE_NAME = 'URLs'
    PURCHASED_COMICS_TABLE_NAME = 'PurchasedComics'

    def __init__(self, db_connection, response_data):

        self.db = db_connection
        self.data = response_data

        self.id = None
        self.modified = None
        self.image_paths = set()  # {image_paths} ... includes thumbnail path as well ...entity_has...
        self.resourceURI = None
        self.thumbnail = None
        self.thumbnailExtension = None
        self.urls = set()  # set of tuples (type, url)
        self.eventDetail = {}  # (eventDetail[eventId] = {title: '', uri: ''})
        self.seriesDetail = {}  # (seriesDetail[seriesId] = {title: '', uri: ''})
        self.storyDetail = {}  # (storyDetail[story_id] = {title: '', type: '', uri: ''})

    ####################################################################################################################
    #
    #                                   MAIN CONTROL FLOW FUNCTIONS
    #
    ####################################################################################################################

    def save_properties(self):
        """
        Maps the json response to member class variables
        """
        pass

    def upload_new_records(self):
        """
        Uploads new records to the database before uploading the entire comic book with relevant foreign keys
        """
        pass

    ####################################################################################################################
    #
    #          ADD NEW JSON RESPONSE DATA TO CLASS VARIABLES
    #
    ####################################################################################################################

    def _save_events(self):
        """
        A resource list containing the events in which this entity relates.
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

    def _save_id(self):
        """
        The unique ID of the comic resource.
        """
        self.id = int(self.data['id'])

    def _save_modified(self):
        """
        The date the resource was most recently modified.
        """

        self.modified = self.convert_to_SQL_date(self.data['modified'])

    def _save_resourceURI(self):
        """
        The canonical URL identifier for this resource.
        """
        self.resourceURI = str(self.data['resourceURI'])

    def _save_stories(self):
        """
        A resource list containing the stories which are related to the entity.
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

    def _save_thumbnail(self):
        """
        The representative image for this comic.
        """
        thumbnail_path = self.data['thumbnail']['path']
        thumbnail_extension = '.' + self.data['thumbnail']['extension']

        self.thumbnail = str(thumbnail_path)
        self.thumbnailExtension = thumbnail_extension

        if self.thumbnail not in self.image_paths:
            self.image_paths.add((self.thumbnail, self.thumbnailExtension))

    def _save_urls(self):
        """
        A set of public web-site URLs for the resource.
        """
        for url in self.data['urls']:
            self.urls.add((url['type'], url['url']))

    ####################################################################################################################
    #
    #                                   ADD NEW RECORDS TO DATABASE
    #
    ####################################################################################################################
    def _add_new_event(self):
        """
        Adds a new event to the comic_books.events table if event record does not already exist
        """
        for event in self.eventDetail:
            event_id = event
            event_title = self.eventDetail[event_id]['title']
            event_uri = self.eventDetail[event_id]['uri']

            self.db.upload_new_record_by_table(self.EVENTS_TABLE_NAME, event_id, event_title, event_uri)

    def _add_new_image(self):
        """
        Adds any image urls to the database that are not currently in the comic_books.Images table
        """

        for image, image_extension in self.image_paths:
            self.db.upload_new_image_record(image, image_extension)

    def _add_new_series(self):
        """
        Adds the series to the comic_books.series table if series record does not already exist.
        """
        for series in self.seriesDetail:
            series_id = series
            series_title = self.seriesDetail[series_id]['title']
            series_uri = self.seriesDetail[series_id]['uri']

            self.db.upload_new_record_by_table(self.SERIES_TABLE_NAME, series_id, series_title, series_uri)

    def _add_new_story(self):
        """
        Creates and commits any new story records to comic_books.stories table
        """

        for story in self.storyDetail:
            story_id = story
            story_title = self.storyDetail[story_id]['title']
            story_type = self.storyDetail[story_id]['type']
            story_resource_uri = self.storyDetail[story_id]['uri']

            self.db.upload_new_story_record(story_id, story_title, story_resource_uri, story_type)

    def _add_new_url(self):
        """
        Adds any new urls without an existing record to the comic_books.URLs table
        """
        for url_type, url_path in self.urls:
            self.db.upload_new_url_record(url_type, url_path)

    ####################################################################################################################
    #
    #                                   UTILITIES
    #
    ####################################################################################################################

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

    @staticmethod
    def convert_to_SQL_date(date_string: str) -> Date:
        """
        Converts Date string formatted "%Y-%m-%dT%H:%M:%S%z" to datetime object compatible with SQL database
        """

        return datetime.datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S%z")

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
