"""
Author: Zane Miller
Email: millerzanem@gmail.com
Date: 04/17/2023
Description: Class drivers for looking up marvel comics with marvel public api
"""
from backend.backendModels.Entity import Entity


class Event(Entity):
    """
    Event object is a map of the marvel public api /events endpoint response model. The Event object is
    responsible for parsing the response data, creating new backendDatabase records for specific entities and creating a new
    Event in the backendDatabase.
    """

    def __init__(self, db_connection, response_data):
        """ Represents an Event based on the marvel character developer api json response model """
        super().__init__(db_connection, response_data)
        self.eventStart = None
        self.eventEnd = None
        self.nextEventDetail = {}
        self.nextEventId = None
        self.previousEventDetail = {}
        self.previousEventId = None

        self.ENTITY_NAME = self.EVENT_ENTITY
        self.EVENT_DEBUG = True

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
            # Unique to Event() class
            self._save_next_previous_events()
            self._save_start_end_dates()

            # From Parent class
            self._save_characters()
            self._save_comics()
            self._save_creators()
            self._save_description()
            self._save_id()
            self._save_modified()
            self._save_resourceURI()
            self._save_stories()
            self._save_thumbnail()
            self._save_title()
            self._save_urls()

    def upload_new_records(self):
        """
        Uploads new records to the backendDatabase before uploading the entire comic book with relevant foreign keys
        """
        # Unique to Event() class
        self._add_new_event()  # modified for next event and previous event

        # From parent class
        self._add_new_character()
        self._add_new_creator()
        self._add_new_comic()
        self._add_new_image()
        self._add_new_series()
        self._add_new_story()
        self._add_new_url()

    def upload_event(self):
        """
        Compiles the Event() entities into params tuple to pass to backendDatabase function for uploading
        complete Event()
        """
        params = (self.id, self.title, self.description, self.resourceURI, self.modified, self.eventStart,
                  self.eventEnd, self.thumbnail, self.nextEventId, self.previousEventId)

        self.db.upload_complete_event(params)

    def upload_event_has_relationships(self):
        """
        Runs through and creates all the events_has_relationships
        """
        self._entity_has_characters()
        self._entity_has_creators()
        self._entity_has_stories()
        self._entity_has_urls()

        self._events_has_comics()  # Comics_has_Events
        self._events_has_series()  # Series_has_Events

    ####################################################################################################################
    #
    #          ADD NEW JSON RESPONSE DATA TO CLASS VARIABLES
    #
    ####################################################################################################################
    def _save_start_end_dates(self):
        """
        Saves the start end date of the Event
        """
        if 'start' in self.data and self.data['start'] is not None:
            self.eventStart = self.convert_eventStartEndDate_to_SQL_date(self.data['start'])

        if 'end' in self.data and self.data['end'] is not None:
            self.eventEnd = self.convert_eventStartEndDate_to_SQL_date(self.data['end'])

    def _save_next_previous_events(self):
        """
        A summary representation of the events which precedes and follows this series.,
        """
        if 'next' in self.data and self.data['next'] is not None:
            next_uri = self.data['next']['resourceURI']
            next_title = self.data['next']['name']
            next_id = self.get_id_from_resourceURI(next_uri)

            if next_id != -1:
                if next_id not in self.nextEventDetail:
                    self.nextEventDetail[next_id] = {'title': str(next_title),
                                                     'uri'  : str(next_uri)}

                self.nextEventId = int(next_id)

        if 'previous' in self.data and self.data['previous'] is not None:
            previous_uri = self.data['previous']['resourceURI']
            previous_title = self.data['previous']['name']
            previous_id = self.get_id_from_resourceURI(previous_uri)

            if previous_id != -1:
                if previous_id not in self.previousEventDetail:
                    self.previousEventDetail[previous_id] = {'title': str(previous_title),
                                                             'uri'  : str(previous_uri)}

                self.previousEventId = int(previous_id)

    ####################################################################################################################
    #
    #                                   ADD NEW RECORDS TO DATABASE
    #
    ####################################################################################################################
    def _add_new_event(self):
        """
        Overrides the parent method to upload nextEvent and previousEvent unique to the
        Event() class
        """
        for next_event in self.nextEventDetail:
            event_id = next_event
            event_title = self.nextEventDetail[event_id]['title']
            event_uri = self.nextEventDetail[event_id]['uri']

            self.db.upload_new_record_by_table(self.ENTITY_NAME, event_id, event_title,
                                               event_uri)

        for previous_event in self.previousEventDetail:
            previous_id = previous_event
            previous_title = self.previousEventDetail[previous_id]['title']
            previous_uri = self.previousEventDetail[previous_id]['uri']

            self.db.upload_new_record_by_table(self.ENTITY_NAME, previous_id, previous_title,
                                               previous_uri)

    ####################################################################################################################
    #
    #                               Events_has_Relationships
    #
    ####################################################################################################################
    def _events_has_comics(self):
        """
        Uploads new record to the Comics_has_Events table
        """
        for comic in self.comicDetail:
            self.db.upload_new_entity_has_events_record(self.COMIC_ENTITY, int(comic), int(self.id))

    def _events_has_series(self):
        """
        Uploads new record to the Series_has_Events table
        """
        for series in self.seriesDetail:
            self.db.upload_new_entity_has_events_record(self.SERIES_ENTITY, int(series), int(self.id))
