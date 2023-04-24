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
    STORY_ENTITY = "Stories"
    COMIC_ENTITY = "Comics"
    SERIES_ENTITY = "Series"
    EVENT_ENTITY = "Events"
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
        self.creatorDetail = {}  # (creatorDetail[creator_id] = {f_name: '', m_name: '', l_name: '', uri: ''})
        self.comicDetail = {}  # (comicDetail[comicId] = {title: '', uri: ''})

        self.characterDetail = {}  # (characterDetail[character_id] = {name: '', uri: ''})
        self.creatorsRoles = {}  # (creatorsRoles[creator_id] = [roles]}) ...entity_has...

        self.description = None  # string, optional

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

    def _save_comics(self):
        """
        Saves the comics related to the creator. If the original number of returned comics is less than the available
        number of comics, function will fetch the remaining comics and add to list.
        """

        # save the ones fetched from the initial creators query
        if self.data['comics']['available'] > 0:
            for comic in self.data['comics']['items']:
                comic_uri = comic['resourceURI']
                comic_title = comic['name']
                comic_id = self.get_id_from_resourceURI(comic_uri)

                if comic_id != -1 and comic_id not in self.comicDetail:
                    self.comicDetail[comic_id] = {'title': comic_title, 'uri': comic_uri}

    def _save_creators(self):
        """
        A resource list containing the creators associated with this comic.
        """
        if 'creators' in self.data and self.data['creators']['available'] > 0:
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
                    if creator_id not in self.creatorsRoles:
                        self.creatorsRoles[creator_id] = [creator_role]
                    else:
                        self.creatorsRoles[creator_id].append(creator_role)

    def _save_description(self):
        """
        The preferred description of the comic.
        """
        if 'description' in self.data:
            self.description = str(self.data['description'])

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

    def _save_series(self):
        """
        A summary representation of the series to which this comic belongs.
        """
        if self.data['series']['available'] > 0:
            if 'series' in self.data and self.data['series']:
                series_uri = self.data['series']['resourceURI']
                series_title = self.data['series']['name']
                series_id = self.get_id_from_resourceURI(series_uri)

                if series_id != -1:
                    if series_id not in self.seriesDetail:
                        self.seriesDetail[series_id] = {'title': series_title, 'uri': series_uri}

                self.seriesId = series_id

    def _save_stories(self):
        """
        A resource list containing the stories which are related to the entity.
        """

        if 'stories' in self.data and self.data['stories']['available'] > 0:
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

    def _save_title(self):
        """
        The canonical title of the resource.
        """
        if 'title' in self.data:
            self.title = str(self.data['title'])

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
    def _add_new_character(self):
        """
        Adds new character to comic_books.characters table if record does not exist
        """

        for character in self.characterDetail:
            character_id = character
            character_name = self.characterDetail[character_id]['name']
            character_resource_uri = self.characterDetail[character_id]['uri']

            self.db.upload_new_character_record(character_id, character_name, character_resource_uri)

    def _add_new_comic(self):
        """
        Uploads any related comic records that do not already exist in the comic_books.comics table
        """
        for comic in self.comicDetail:
            comic_id = comic
            comic_title = self.comicDetail[comic_id]['title']
            comic_uri = self.comicDetail[comic_id]['uri']

            self.db.upload_new_related_comic_record(comic_id, comic_title, comic_uri)

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
