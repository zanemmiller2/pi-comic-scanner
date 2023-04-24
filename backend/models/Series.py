"""
Author: Zane Miller
Email: millerzanem@gmail.com
Date: 04/17/2023
Description: Class drivers for looking up marvel comics with marvel public api
"""
from backend.models.Entity import Entity


class Series(Entity):

    def __init__(self, db_connection, response_data):
        super().__init__(db_connection, response_data)
        self.title = None
        self.startYear = None
        self.endYear = None
        self.rating = None
        self.type = None
        self.nextSeriesDetail = {}  # (nextSeries[seriesId] = {title: '', uri: ''})
        self.previousSeriesDetail = {}  # (previousSeries[seriesId] = {title: '', uri: ''})

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
            # Unique to Series() class
            self._save_end_year()
            self._save_next_series()
            self._save_previous_series()
            self._save_rating()
            self._save_start_year()
            self._save_type()
            # From Parent class
            self._save_characters()
            self._save_comics()
            self._save_creators()
            self._save_description()
            self._save_events()
            self._save_id()
            self._save_modified()
            self._save_resourceURI()
            self._save_stories()
            self._save_thumbnail()
            self._save_title()
            self._save_urls()

    def upload_new_records(self):
        """
        Uploads new records to the database before uploading the entire comic book with relevant foreign keys
        """
        # Unique to Series() class

        # From parent class
        self._add_new_character()
        self._add_new_creator()
        self._add_new_comic()
        self._add_new_event()
        self._add_new_image()
        self._add_new_series()
        self._add_new_story()
        self._add_new_url()

    def upload_series(self):
        """
        Compiles the Series() entities into params tuple to pass to database function for uploading
        complete Series()
        """
        pass

    def upload_series_has_relationships(self):
        """
        Runs through and creates all the series_has_relationships
        """
        self._series_has_characters()
        self._series_has_creators()
        self._series_has_events()
        self._series_has_stories()
        self._series_has_urls()

    ####################################################################################################################
    #
    #          ADD NEW JSON RESPONSE DATA TO CLASS VARIABLES
    #
    ####################################################################################################################

    def _save_end_year(self):
        """
        The last year of publication for the series (conventionally, 2099 for ongoing series).
        """
        self.endYear = int(self.data['endYear'])

    def _save_next_series(self):
        """
        A summary representation of the series which follows this series.,
        """
        if self.data['next']:
            next_uri = self.data['next']['resourceURI']
            next_title = self.data['next']['name']
            next_id = self.get_id_from_resourceURI(next_uri)

            if next_id != -1:
                if next_id not in self.nextSeriesDetail:
                    self.nextSeriesDetail[next_id] = {'title': next_title,
                                                      'uri'  : next_uri}

    def _save_previous_series(self):
        """
        A summary representation of the series which preceded this series.
        """
        if self.data['previous']:
            previous_uri = self.data['previous']['resourceURI']
            previous_title = self.data['next']['name']
            previous_id = self.get_id_from_resourceURI(previous_uri)

            if previous_id != -1:
                if previous_id not in self.previousSeriesDetail:
                    self.previousSeriesDetail[previous_id] = {'title': previous_title,
                                                              'uri'  : previous_uri}

    def _save_rating(self):
        """
        The age-appropriateness rating for the series.
        """
        self.rating = str(self.data['rating'])

    def _save_start_year(self):
        """
        The first year of publication for the series.
        """
        self.startYear = int(self.data['startYear'])

    def _save_type(self):
        """
        The type of the series.
        """
        self.type = int(self.data['type'])

    ####################################################################################################################
    #
    #                                   ADD NEW RECORDS TO DATABASE
    #
    ####################################################################################################################

    def _add_new_series(self):
        """
        Overrides the parent method to upload nextSeries and previousSeries unique to the
        Series() class
        """

        for next_series in self.nextSeriesDetail:
            series_id = next_series
            series_title = self.nextSeriesDetail[series_id]['title']
            series_uri = self.nextSeriesDetail[series_id]['uri']

            self.db.upload_new_record_by_table(self.SERIES_TABLE_NAME, series_id, series_title,
                                               series_uri)

        for previous_series in self.previousSeriesDetail:
            series_id = previous_series
            series_title = self.previousSeriesDetail[series_id]['title']
            series_uri = self.previousSeriesDetail[series_id]['uri']

            self.db.upload_new_record_by_table(self.SERIES_TABLE_NAME, series_id, series_title,
                                               series_uri)

    ####################################################################################################################
    #
    #                               Comics_has_Relationships
    #
    ####################################################################################################################

    def _series_has_characters(self):
        """
        Upload new record in Series_has_Characters table
        """
        for characterId in self.characterDetail:
            self.db.upload_new_entity_has_characters_record(self.SERIES_ENTITY, int(self.id), int(characterId))

    def _series_has_creators(self):
        """
        Upload new record in Series_has_Creators table
        """

    def _series_has_events(self):
        """
        Upload new record in Series_has_Events table
        """
        pass

    def _series_has_stories(self):
        """
        Upload new record in Series_has_Events table
        """
        pass

    def _series_has_urls(self):
        """
        Upload new record in Series_has_URLs table
        """
        pass
