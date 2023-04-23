from backend.models.Entity import Entity

CREATORS_URL = "https://gateway.marvel.com/v1/public/creators"
STORY_ENTITY = "stories"
COMIC_ENTITY = "comics"
SERIES_ENTITY = "series"
EVENT_ENTITY = "events"
MAX_RESOURCE_LIMIT = 100


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
        self.comicDetail = {}  # (comicDetail[comicId] = {title: '', uri: ''})
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
            self._save_id()
            self._save_modified()
            self._save_resourceURI()
            self._save_thumbnail()
            self._save_urls()

            # Unique to Creator() class
            self._save_comics()
            self._save_events()
            self._save_firstName()
            self._save_lastName()
            self._save_middleName()
            self._save_series()
            self._save_stories()
            self._save_suffix()

    def upload_new_records(self):
        """
        Uploads new records to the database before uploading the entire comic book with relevant foreign keys
        """

        # Unique to Creator() class
        self._add_new_comic()

        # From parent class
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
        self._creators_has_events()
        self._creators_has_series()
        self._creators_has_stories()
        self._creators_has_URLs()
        self._creators_has_comics()

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

    def _save_series(self):
        """
        Saves the series related to the creator. If the original number of returned series is less than the available
        number of series, function will fetch the remaining series and add to list.
        """

        # save the ones fetched from the initial creators query
        if self.data['series']['available'] > 0:
            for series in self.data['series']['items']:
                series_uri = series['resourceURI']
                series_title = series['name']
                series_id = self.get_id_from_resourceURI(series_uri)

                if series_id != -1 and series_id not in self.seriesDetail:
                    self.seriesDetail[series_id] = {'title': series_title, 'uri': series_uri}

    def _save_comics(self):
        """
        Saves the comics related to the creator. If the original number of returned comics is less than the available
        number of comics, function will fetch the remaining comics and add to list.
        """
        total_available_comics = self.data['comics']['available']
        comics_offset = 0

        # save the ones fetched from the initial creators query
        if self.data['comics']['available'] > 0:
            for comic in self.data['comics']['items']:
                comic_uri = comic['resourceURI']
                comic_title = comic['name']
                comic_id = self.get_id_from_resourceURI(comic_uri)
                comics_offset += 1

                if comic_id != -1 and comic_id not in self.comicDetail:
                    self.comicDetail[comic_id] = {'title': comic_title, 'uri': comic_uri}

    ####################################################################################################################
    #
    #                                   ADD NEW RECORDS TO DATABASE
    #
    ####################################################################################################################

    def _add_new_comic(self):
        """
        Uploads any related comic records that do not already exist in the comic_books.comics table
        """
        for comic in self.comicDetail:
            comic_id = comic
            comic_title = self.comicDetail[comic_id]['title']
            comic_uri = self.comicDetail[comic_id]['uri']

            self.db.upload_new_related_comic_record(comic_id, comic_title, comic_uri)

    ####################################################################################################################
    #
    #                               Creators_has_Relationships
    #
    ####################################################################################################################

    def _creators_has_stories(self):
        """
        Upload new record in Creators_has_Stories table
        """
        for story in self.storyDetail:
            self.db.upload_new_creators_has_stories_record(int(self.id), int(story))

    def _creators_has_URLs(self):
        """
        Upload new record in Creators_has_URLs table
        """
        for url_type, url_str in self.urls:
            self.db.upload_new_creators_has_urls_record(int(self.id), str(url_str))

    def _creators_has_comics(self):
        """
        Upload new record in Comics_has_Creators table
        """
        for comic in self.comicDetail:
            self.db.upload_new_comics_has_creators_record(int(comic), int(self.id))

    def _creators_has_events(self):
        """
        Upload new record in Creators_has_events table
        """
        for event in self.eventDetail:
            self.db.upload_new_creators_has_events_record(int(self.id), int(event))

    def _creators_has_series(self):
        """
        Upload new record in Creators_has_series table
        """
        for series in self.seriesDetail:
            self.db.upload_new_creators_has_series_record(int(self.id), int(series))
