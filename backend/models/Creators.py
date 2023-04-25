"""
Author: Zane Miller
Email: millerzanem@gmail.com
Date: 04/17/2023
Description: Class drivers for looking up marvel comics with marvel public api
"""

from backend.models.Entity import Entity


class Creator(Entity):
    """
    Creator object is a map of the marvel public api /creators endpoint response model. The Creator object is
    responsible for parsing the response data, creating new database records for specific entities and creating or
    updating a new Creator in the database.
    """

    def __init__(self, db_connection, response_data):
        """ Represents a Creator book based on the marvel creator developer api json response model """
        super().__init__(db_connection, response_data)
        self.firstName = None
        self.middleName = None
        self.lastName = None
        self.suffix = None

        self.ENTITY_NAME = self.CREATOR_ENTITY
        self.CREATOR_DEBUG = True

    ####################################################################################################################
    #
    #                                   MAIN CONTROL FLOW FUNCTIONS
    #
    ####################################################################################################################

    def save_properties(self):
        """
        Maps the json response to member class variables
        """
        if self.data:
            # From Parent Class
            self._save_comics()
            self._save_events()
            self._save_id()
            self._save_modified()
            self._save_resourceURI()
            self._save_series()
            self._save_stories()
            self._save_thumbnail()
            self._save_urls()

            # Unique to Creator() class
            self._save_firstName()
            self._save_lastName()
            self._save_middleName()
            self._save_suffix()

    def upload_new_records(self):
        """
        Uploads new records to the database before uploading the entire comic book with relevant foreign keys
        """

        # Unique to Creator() class

        # From parent class
        self._add_new_comic()
        self._add_new_event()
        self._add_new_image()
        self._add_new_series()
        self._add_new_story()
        self._add_new_url()

    def upload_creator(self):
        """
        Compiles the Creator entities into params tuple to pass to database function for uploading complete Creator
        """
        params = (self.id, self.firstName, self.middleName, self.lastName, self.suffix, self.modified,
                  self.resourceURI, self.thumbnail, self.thumbnailExtension, self.firstName, self.middleName,
                  self.lastName, self.suffix, self.modified, self.resourceURI, self.thumbnail, self.thumbnailExtension)

        self.db.upload_complete_creator(params)

    def upload_creator_has_relationships(self):
        """
        Runs through and creates all the comics_has_relationships
        """
        self._entity_has_urls()

        self._creators_has_events()  # Events_has_Series
        self._creators_has_series()  # Series_has_Creators
        self._creators_has_comics()  # Comics_has_Creators
        self._creators_has_stories()  # Stories_has_Creators

    ####################################################################################################################
    #
    #                          ADD NEW JSON RESPONSE DATA TO CLASS VARIABLES
    #
    ####################################################################################################################

    def _save_firstName(self):
        """
        Saves the first name of the creator
        """
        self.firstName = self.data['firstName']

    def _save_lastName(self):
        """
        Saves the last name of the creator
        """
        self.lastName = self.data['lastName']

    def _save_middleName(self):
        """
        Saves the middle name of the creator
        """
        self.middleName = self.data['middleName']

    def _save_suffix(self):
        """
        Saves the name suffix of the creator
        """
        self.suffix = self.data['suffix']
    ####################################################################################################################
    #
    #                               Creators_has_Relationships
    #
    ####################################################################################################################

    def _creators_has_comics(self):
        """
        Upload new record in Comics_has_Creators table
        """
        for comic in self.comicDetail:
            self.db.upload_new_entity_has_creators_record(self.COMIC_ENTITY, int(comic), int(self.id))

    def _creators_has_events(self):
        """
        Upload a new record to the Events_has_Creators table
        """

        for event in self.eventDetail:
            self.db.upload_new_entity_has_creators_record(self.EVENT_ENTITY, int(event), int(self.id))

    def _creators_has_series(self):
        """
        Upload new record in Series_has_Creators table
        """
        for series in self.seriesDetail:
            self.db.upload_new_entity_has_creators_record(self.SERIES_ENTITY, int(series), int(self.id))

    def _creators_has_stories(self):
        """
        Upload a new record to the Stories_has_Creators table
        """
        for story in self.storyDetail:
            self.db.upload_new_entity_has_creators_record(self.STORY_ENTITY, int(story), int(self.id))


