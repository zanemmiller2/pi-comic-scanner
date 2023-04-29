"""
Author: Zane Miller
Email: millerzanem@gmail.com
Date: 04/25/2023
Description: Class drivers for looking up marvel comics with marvel public api
"""

from backend.models.Entity import Entity


class Character(Entity):
    """
    Character object is a map of the marvel public api /characters endpoint response model. The Character object is
    responsible for parsing the response data, creating new database records for specific entities and creating a new
    Character in the database.
    """

    def __init__(self, db_connection, response_data):
        """ Represents a Character based on the marvel character developer api json response model """
        super().__init__(db_connection, response_data)
        self.name = None
        self.ENTITY_NAME = self.CHARACTER_ENTITY

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
            # Unique to Character() class
            self._save_name()

            # From Parent class
            self._save_comics()
            self._save_description()
            self._save_events()
            self._save_id()
            self._save_modified()
            self._save_resourceURI()
            self._save_series()
            self._save_stories()
            self._save_thumbnail()
            self._save_urls()

    def upload_new_records(self):
        """
        Uploads new records to the database before uploading the entire Character with relevant foreign keys
        """
        self._add_new_comic()
        self._add_new_event()
        self._add_new_image()
        self._add_new_series()
        self._add_new_story()
        self._add_new_url()

    def upload_character(self):
        """
        Compiles the character entities into params tuple to pass to database function for uploading complete character
        """

        params = (self.id, self.name, self.description, self.modified, self.resourceURI, self.thumbnail)

        self.db.upload_complete_character(params)

    def upload_character_has_relationships(self):
        """
        Runs through and creates all the characters_has_relationships
        """
        self._entity_has_urls()

        self._characters_has_comics()  # Comics_has_Characters
        self._characters_has_events()  # Events_has_Characters
        self._characters_has_series()  # Series_has_Characters
        self._characters_has_stories()  # Stories_has_Characters

    ####################################################################################################################
    #
    #          ADD NEW JSON RESPONSE DATA TO CLASS VARIABLES
    #
    ####################################################################################################################
    def _save_name(self):
        """
        Saves the name of the Character
        """
        if 'name' in self.data and self.data['name'] is not None:
            self.name = str(self.data['name'])

    ####################################################################################################################
    #
    #                               Characters_has_Relationships
    #
    ####################################################################################################################
    def _characters_has_comics(self):
        """
        Upload new record in Comics_has_Characters table
        """
        for comic in self.comicDetail:
            self.db.upload_new_entity_has_characters_record(self.COMIC_ENTITY, int(comic), int(self.id))

    def _characters_has_events(self):
        """
        Upload a new record to the Events_has_Characters table
        """
        for event in self.eventDetail:
            self.db.upload_new_entity_has_characters_record(self.EVENT_ENTITY, int(event), int(self.id))

    def _characters_has_series(self):
        """
        Upload new record in Series_has_Characters table
        """
        for series in self.seriesDetail:
            self.db.upload_new_entity_has_characters_record(self.SERIES_ENTITY, int(series), int(self.id))

    def _characters_has_stories(self):
        """
        Upload a new record to the Stories_has_Characters table
        """
        for story in self.storyDetail:
            self.db.upload_new_entity_has_characters_record(self.STORY_ENTITY, int(story), int(self.id))


