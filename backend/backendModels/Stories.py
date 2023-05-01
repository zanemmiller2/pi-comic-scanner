"""
Author: Zane Miller
Email: millerzanem@gmail.com
Date: 04/17/2023
Description: Class drivers for looking up marvel comics with marvel public api
"""

from backend.backendModels.Entity import Entity


class Story(Entity):
    """
    Story object is a map of the marvel public api /stories endpoint response model. The Story object is
    responsible for parsing the response data, creating new backendDatabase records for specific entities and creating or
    updating a new Story in the backendDatabase.
    """

    def __init__(self, db_connection, response_data):
        """ Represents a Story book based on the marvel story developer api json response model """
        super().__init__(db_connection, response_data)

        self.ENTITY_NAME = self.STORY_ENTITY

    ####################################################################################################################
    #
    #                                   MAIN CONTROL FLOW FUNCTIONS
    #
    ####################################################################################################################
    def save_properties(self):
        """
        Maps the json response to member class variables
        """
        # From Parent Class
        self._save_characters()
        self._save_comics()
        self._save_creators()
        self._save_description()
        self._save_events()
        self._save_id()
        self._save_modified()
        self._save_originalIssueId()
        self._save_resourceURI()
        self._save_series()
        self._save_thumbnail()
        self._save_title()
        self._save_type()

    def upload_new_records(self):
        """
        Uploads new records to the backendDatabase before uploading the entire comic book with relevant foreign keys
        """
        # From parent class
        self._add_new_character()
        self._add_new_creator()
        self._add_new_comic()
        self._add_new_event()
        self._add_new_image()
        self._add_new_series()

    def upload_story(self):
        """
        Compiles the Creator entities into params tuple to pass to backendDatabase function for uploading complete Creator
        """
        params = (self.id, self.title, self.description, self.resourceURI, self.type, self.modified, self.thumbnail)

        self.db.upload_complete_story(params)

    def upload_story_has_relationships(self):
        """
        Runs through and creates all the comics_has_relationships
        """
        self._entity_has_characters()
        self._entity_has_creators()

        self._stories_has_series()  # Series_has_Stories
        self._stories_has_events()  # Events_has_Stories
        self._stories_has_comics()  # Comics_has_Stories

    ####################################################################################################################
    #
    #                               Stories_has_Relationships
    #
    ####################################################################################################################
    def _stories_has_series(self):
        """
        Uploads a new Series_has_Stories record
        """
        for series in self.seriesDetail:
            self.db.upload_new_entity_has_stories_record(self.SERIES_ENTITY, int(series), int(self.id))

    def _stories_has_events(self):
        """
        Uploads a new Events_has_Stories record
        """
        for event in self.eventDetail:
            self.db.upload_new_entity_has_stories_record(self.EVENT_ENTITY, int(event), int(self.id))

    def _stories_has_comics(self):
        """
        Uploads a new Comics_has_Stories record
        """
        for comic in self.comicDetail:
            self.db.upload_new_entity_has_stories_record(self.COMIC_ENTITY, int(comic), int(self.id))

