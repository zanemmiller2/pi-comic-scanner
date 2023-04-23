"""
Author: Zane Miller
Email: millerzanem@gmail.com
Date: 04/21/2023
Description: Class drivers for database functions
"""
import MySQLdb

from keys import db_credentials


class InvalidCursorExecute(Exception):
    """ cursor.execute failed """
    pass


class DB:
    """
    DB Object that represents a connection and cursor for the provided database and credentials
    """

    def __init__(self):
        """
        Represents a DB object with username, hostname, password, database name, cursor, and connection
        """
        # self._host = input("DB Host: ")
        # self._user = input("DB User: ")
        # self._passwd = input("DB Password: ")
        # self._db_name = input("DB Name: ")

        self._host = db_credentials.host
        self._user = db_credentials.user
        self._passwd = db_credentials.passwd
        self._db = db_credentials.db

        self._connection = self._connect_to_database()
        self.cursor = self._connection.cursor(MySQLdb.cursors.DictCursor)

    '''
    ####################################################################################################################
    #
    #                                       GET FROM DATABASE
    #
    ####################################################################################################################
    '''
    def get_upcs_from_buffer(self):
        """
        Selects all entries from scanned_upc_codes from comic_books database
        :return: db cursor
        """
        if self._connection is None:
            print(
                "No connection to the database found! Have you called connect_to_database() first?"
            )
            return None

        query = "SELECT upc_code, date_uploaded FROM scanned_upc_codes;"

        try:
            print("Executing %s", query)
            self.cursor.execute(query)
            self._commit_to_db()
        except InvalidCursorExecute:
            print(f"GET UPCS ERROR")
            self._connection.rollback()

        return self.cursor.fetchall()

    def get_stale_creators(self):
        """
        Selects the Creators records that have a modified date older than a year ago or no modified date at all.
        Creators with no modified date were most likely added as a bare bones foreign key dependency.
        :return: set of creator ids to update
        """
        query = "SELECT id from Creators " \
                "WHERE " \
                "Creators.modified IS NULL OR " \
                "YEAR(CURRENT_TIMESTAMP) - YEAR(Creators.modified) > 1;"

        try:
            print("Executing %s", query)
            self.cursor.execute(query)
            self._commit_to_db()
        except InvalidCursorExecute:
            print(f"GET STALE CREATORS ERROR")
            self._connection.rollback()

        return self.cursor.fetchall()

    '''
    ####################################################################################################################
    #
    #                                       UPLOAD TO DATABASE
    #
    ####################################################################################################################
    '''

    ################################################################
    #  Complete Entities
    ################################################################

    def upload_upc_to_buffer(self, params: tuple[str, str]):
        """
        Uploads a tuple of strings (upc and YYYY-MM-DD) to the scanned_upc_codes table in the comic_books database
        :param params: (upc: str, YYYY-MM-DD: str)
        :return: cursor object from connection
        """

        query = "INSERT INTO comic_books.scanned_upc_codes(upc_code, date_uploaded) VALUES (%s, %s);"

        try:
            print("Executing %s with %s" % (query, params))
            self.cursor.execute(query, params)
            self._commit_to_db()
        except InvalidCursorExecute:
            print(f"UPC {params[0]} NOT UPLOADED TO BUFFER")
            self._connection.rollback()

    def upload_complete_comic_book(self, params: tuple):
        """
        Inserts a new comic book record in the comic_books.comics table
        :param params: a tuple of comic book column values
        """
        query = f"INSERT INTO Comics " \
                f"(id, digitalId, title, issueNumber, variantDescription, description, modified, isbn, upc, diamondCode, " \
                f"ean, issn, format, pageCount, textObjects, resourceURI, detailURL, purchaseURL, readerURL, inAppLink, " \
                f"onSaleDate, focDate, unlimitedDate, digitalPurchaseDate, printPrice, digitalPurchasePrice, seriesId, " \
                f"thumbnail, thumbnailExtension, originalIssue) " \
                f"VALUES " \
                f"(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, " \
                f"%s, %s, %s, %s, %s);"

        try:
            print("Executing %s with %s" % (query, params))
            self.cursor.execute(query, params)
            self._commit_to_db()
        except InvalidCursorExecute:
            print(f"COMIC {params[0]} : {params[2]} NOT UPLOADED TO Comics TABLE")
            self._connection.rollback()

    def upload_complete_creator(self, params: tuple):
        """
        Updates/Inserts a Creator in the comic_books.creators table
        :param params: a tuple of creator column values
        """

        query = f"INSERT INTO Creators " \
                f"(id, firstName, middleName, lastName, suffix, modified, resourceURI, thumbnail, thumbnailExtension) " \
                f"VALUES " \
                f"(%s, %s, %s, %s, %s, %s, %s, %s, %s) " \
                f"ON DUPLICATE KEY UPDATE " \
                f"firstName=%s, middleName=%s, lastName=%s, suffix=%s, modified=%s, resourceURI=%s, thumbnail=%s, " \
                f"thumbnailExtension=%s;"

        try:
            print("Executing %s with %s" % (query, params))
            self.cursor.execute(query, params)
            self._commit_to_db()
        except InvalidCursorExecute:
            print(f"CREATOR {params[0]} : {params[2]} NOT UPLOADED TO Comics TABLE")
            self._connection.rollback()

    def upload_complete_purchased_comic(self, params: tuple):
        """
        Uploads a complete record to the PurchasedComics Table
        """
        query = f"INSERT INTO PurchasedComics " \
                f"(comicId, purchaseDate, purchasePrice, purchaseType) " \
                f"VALUES " \
                f"(%s, %s, %s, %s) " \
                f"ON DUPLICATE KEY UPDATE " \
                f"purchasedDate = COALESCE (VALUES(purchasedDate), %s)," \
                f"purchasePrice = COALESCE (VALUES(purchasePrice), %s)," \
                f"purchaseType = COALESCE (VALUES(purchaseType), %s);"
        try:
            print("Executing %s with %s" % (query, params))
            self.cursor.execute(query, params)
            self._commit_to_db()
        except InvalidCursorExecute:
            print(f"PURCHASED COMIC {params[0]} NOT UPLOADED TO PurchasedComics TABLE")
            self._connection.rollback()

    ################################################################
    #  Foreign Key Dependencies -- partial records
    ################################################################

    def upload_new_image_record(self, image_path: str, image_extension: str):
        """
        Uploads a new image path to comic_books.image_paths if image path does not already exist in database
        :param image_path: string of the full image path to upload
        :param image_extension: extension for the image path
        """

        query = "INSERT INTO Images (path, pathExtension) SELECT %s, %s WHERE NOT EXISTS(SELECT * FROM Images WHERE path=%s);"
        params = (image_path, image_extension, image_path)

        try:
            print("Executing %s with %s" % (query, params))
            self.cursor.execute(query, params)
            self._commit_to_db()
        except InvalidCursorExecute:
            print(f"IMAGE {image_path + image_extension} NOT UPLOADED TO Images TABLE")
            self._connection.rollback()

    def upload_new_url_record(self, url_type: str, url_path: str):
        """
        Uploads a new url record to comic_books.URLs if URL does not already exist in database
        :param url_type: string of the url type description
        :param url_path: string of the full url to upload
        """

        query = "INSERT INTO URLs (type, url) SELECT %s, %s WHERE NOT EXISTS (SELECT * FROM URLs WHERE type=%s AND url=%s);"
        params = (url_type, url_path, url_type, url_path)

        try:
            print("Executing %s with %s" % (query, params))
            self.cursor.execute(query, params)
            self._commit_to_db()
        except InvalidCursorExecute:
            print(f"URL {url_type} : {url_path} NOT UPLOADED TO URLs TABLE")
            self._connection.rollback()

    def upload_new_creator_record(
            self, creator_id: int, first_name: str, middle_name: str,
            last_name: str, resource_uri: str
    ):
        """
        Uploads a new creator record to comic_books.creators if Creator does not already exist in database
        :param creator_id: The unique ID of the creator resource.
        :param first_name: The first name of the creator.
        :param middle_name: The middle name of the creator.
        :param last_name: The last name of the creator.
        :param resource_uri: The canonical URL identifier for this resource.
        """

        query = "INSERT INTO Creators (id, firstName, MiddleName, LastName, resourceURI) " \
                "SELECT %s, %s, %s, %s, %s WHERE NOT EXISTS (SELECT * FROM Creators WHERE id=%s);"

        params = (creator_id, first_name, middle_name, last_name, resource_uri, creator_id)

        try:
            print("Executing %s with %s" % (query, params))
            self.cursor.execute(query, params)
            self._commit_to_db()
        except InvalidCursorExecute:
            print(f"CREATOR {creator_id} - {first_name + middle_name + last_name} NOT UPLOADED TO Creators TABLE")
            self._connection.rollback()

    def upload_new_character_record(self, character_id: int, character_name: str, character_uri: str):
        """
        Uploads a new character record to comic_books.characters if URL does not already exist in database
        :param character_id: The unique ID of the character resource.
        :param character_name: The name of the character.
        :param character_uri: The canonical URL identifier for this resource.
        """

        query = "INSERT INTO Characters (id, name, resourceURI) " \
                "SELECT %s, %s, %s WHERE NOT EXISTS (SELECT * FROM Characters WHERE id=%s);"

        params = (character_id, character_name, character_uri, character_id)

        try:
            print("Executing %s with %s" % (query, params))
            self.cursor.execute(query, params)
            self._commit_to_db()
        except InvalidCursorExecute:
            print(f"CHARACTER {character_id} - {character_name} NOT UPLOADED TO Characters TABLE")
            self._connection.rollback()

    def upload_new_story_record(self, story_id: int, story_title: str, story_uri: str, story_type: str):
        """
        Uploads a new story record to comic_books.stories if story does not already exist in database
        :param story_id: The unique ID of the story resource.
        :param story_title: The story title.
        :param story_uri: The canonical URL identifier for this resource.
        :param story_type: The story type e.g. interior story, cover, text story.
        """

        query = "INSERT INTO Stories (id, title, resourceURI, type) " \
                "SELECT %s, %s, %s, %s WHERE NOT EXISTS (SELECT * FROM Stories WHERE id=%s);"

        params = (story_id, story_title, story_uri, story_type, story_id)

        try:
            print("Executing %s with %s" % (query, params))
            self.cursor.execute(query, params)
            self._commit_to_db()
        except InvalidCursorExecute:
            print(f"STORY {story_id} : {story_title} NOT UPLOADED TO Stories TABLE")
            self._connection.rollback()

    def upload_new_variants_record(
            self, variant_id: int, variant_title: str, variant_uri: str, issue_number: float, is_variant: bool
    ):
        """
        Uploads a new story record to comic_books.stories if story does not already exist in database
        :param variant_id: The unique ID of the comic resource.
        :param variant_title: The variant comic title.
        :param variant_uri: The canonical URL identifier for this resource.
        :param issue_number: The issue number of the variant comic in the series
        :param is_variant: boolean value denoting if the comic is a variant
        """

        query = "INSERT INTO Comics (id, title, resourceURI, issueNumber, isVariant) " \
                "SELECT %s, %s, %s, %s, %s WHERE NOT EXISTS (SELECT * FROM Comics WHERE id=%s);"

        params = (variant_id, variant_title, variant_uri, issue_number, is_variant, variant_id)

        try:
            print("Executing %s with %s" % (query, params))
            self.cursor.execute(query, params)
            self._commit_to_db()
        except InvalidCursorExecute:
            print(f"VARIANT COMIC {variant_id} : {variant_title} NOT UPLOADED TO Comics TABLE")
            self._connection.rollback()

    def upload_new_related_comic_record(self, comic_id: int, comic_title: str, comic_uri: str):
        """
        Uploads a new comic with id, title and uri to the comic_books.comics table
        :param comic_id: The unique ID of the comic resource.
        :param comic_title: The comic title.
        :param comic_uri: The canonical URL identifier for this resource.
        """
        query = "INSERT INTO Comics (id, title, resourceURI) " \
                "SELECT %s, %s, %s WHERE NOT EXISTS (SELECT * FROM Comics WHERE id=%s);"

        params = (comic_id, comic_title, comic_uri, comic_id)

        try:
            print("Executing %s with %s" % (query, params))
            self.cursor.execute(query, params)
            self._commit_to_db()
        except InvalidCursorExecute:
            print(f"COMIC {comic_id} : {comic_title} NOT UPLOADED TO Comics TABLE")
            self._connection.rollback()

    ################################################################
    #  GENERIC UTILITY FOR Events and Series
    ################################################################
    def upload_new_record_by_table(self, table_name: str, entity_id: str, entity_title: str, entity_uri: str):
        """
        Uploads a new record to comic_books.table_name (Events, Series)
        if record does not already exist in database using id, title, and uri
        :param table_name: the name of the table in the comic_books database
        :param entity_id: The unique ID of the resource.
        :param entity_title: The title of the entity.
        :param entity_uri: The canonical URL identifier for this resource.
        """

        query = f"INSERT INTO {table_name} (id, title, resourceURI) " \
                f"SELECT %s, %s, %s WHERE NOT EXISTS (SELECT * FROM {table_name} WHERE id=%s);"
        params = (entity_id, entity_title, entity_uri, entity_id)

        try:
            print("Executing %s with %s" % (query, params))
            self.cursor.execute(query, params)
            self._commit_to_db()
        except InvalidCursorExecute:
            print(f"NEW RECORD {entity_id} : {entity_title} NOT UPLOADED TO {table_name} TABLE")
            self._connection.rollback()

    '''
    ####################################################################################################################
    #
    #                                       ADD NEW ENTITY_HAS_RELATIONSHIPS
    #
    ####################################################################################################################
    '''

    ################################################################
    #  COMICS_has
    ################################################################
    def upload_new_comics_has_creators_record(self, comic_id: int, creator_id: int, creator_role: str = None):
        """
        Creates a new Comics_has_Creators record if the comic_id and character_id aren't already related with the
        creator_role
        :param comic_id: The unique ID of the comic resource.
        :param creator_id: The unique ID of the creator resource.
        :param creator_role: The role of the creator in the parent entity.
        """

        query = "INSERT INTO Comics_has_Creators (comicId, creatorId, creatorRole) VALUES (%s, %s, %s)" \
                "ON DUPLICATE KEY UPDATE creatorRole = COALESCE (VALUES(creatorRole), %s);"
        params = (comic_id, creator_id, creator_role, creator_role)

        try:
            print("Executing %s with %s" % (query, params))
            self.cursor.execute(query, params)
            self._commit_to_db()
        except InvalidCursorExecute:
            print(
                f"COMIC : CREATOR M:M RELATIONSHIP {comic_id} : {creator_id} WITH "
                f"ROLE {creator_role} NOT UPLOADED TO Comics_has_Creator TABLE"
            )
            self._connection.rollback()

    def upload_new_comics_has_images_record(self, comic_id: int, image_path: str):
        """
        Creates a new Comics_has_Creators record if the comic_id and image_path aren't already related
        :param comic_id: The unique ID of the comic resource.
        :param image_path: The full path of the image resource
        """

        query = "INSERT INTO Comics_has_Images (comicId, imagePath) SELECT %s, %s WHERE NOT EXISTS " \
                "(SELECT * FROM Comics_has_Images WHERE comicId=%s AND imagePath=%s);"
        params = (comic_id, image_path, comic_id, image_path)

        try:
            print("Executing %s with %s" % (query, params))
            self.cursor.execute(query, params)
            self._commit_to_db()
        except InvalidCursorExecute:
            print(
                f"COMIC : IMAGE M:M RELATIONSHIP {comic_id} : {image_path} WITH NOT UPLOADED TO Comics_has_Images TABLE"
            )
            self._connection.rollback()

    def upload_new_comics_has_urls_record(self, comic_id: int, url: str):
        """
        Creates a new Comics_has_Stories record if the comic_id and story_id aren't already related
        :param comic_id: The unique ID of the comic resource.
        :param url: A full URL (including scheme, domain, and path) related to the comic.
        """

        query = "INSERT INTO Comics_has_URLs (comicId, url) SELECT %s, %s WHERE NOT EXISTS " \
                "(SELECT * FROM Comics_has_URLs WHERE comicId=%s AND url=%s);"
        params = (comic_id, url, comic_id, url)

        try:
            print("Executing %s with %s" % (query, params))
            self.cursor.execute(query, params)
            self._commit_to_db()
        except InvalidCursorExecute:
            print(f"COMIC : URL M:M RELATIONSHIP {comic_id} : {url} WITH NOT UPLOADED TO Comics_has_URL TABLE")
            self._connection.rollback()

    def upload_new_comics_has_characters_record(self, comic_id: int, character_id: int):
        """
        Creates a new Comics_has_Characters record if the comic_id and character_id aren't already related
        :param comic_id: The unique ID of the comic resource.
        :param character_id: The unique ID of the character resource.
        """

        query = "INSERT INTO Comics_has_Characters (comicId, characterId) SELECT %s, %s WHERE NOT EXISTS " \
                "(SELECT * FROM Comics_has_Characters WHERE comicId=%s AND characterId=%s);"
        params = (comic_id, character_id, comic_id, character_id)

        try:
            print("Executing %s with %s" % (query, params))
            self.cursor.execute(query, params)
            self._commit_to_db()
        except InvalidCursorExecute:
            print(
                f"COMIC : CHARACTER M:M RELATIONSHIP {comic_id} : {character_id} WITH NOT UPLOADED TO Comics_has_Characters TABLE"
            )
            self._connection.rollback()

    def upload_new_comics_has_events_record(self, comic_id: int, event_id: int):
        """
        Creates a new Comics_has_Events record if the comic_id and event_id aren't already related
        :param comic_id: The unique ID of the comic resource.
        :param event_id: The unique ID of the event resource.
        """

        query = "INSERT INTO Comics_has_Events (comicId, eventId) SELECT %s, %s WHERE NOT EXISTS " \
                "(SELECT * FROM Comics_has_Events WHERE comicId=%s AND eventId=%s);"
        params = (comic_id, event_id, comic_id, event_id)

        try:
            print("Executing %s with %s" % (query, params))
            self.cursor.execute(query, params)
            self._commit_to_db()
        except InvalidCursorExecute:
            print(
                f"COMIC : EVENTS M:M RELATIONSHIP {comic_id} : {event_id} WITH NOT UPLOADED TO Comics_has_Events TABLE"
            )
            self._connection.rollback()

    def upload_new_comics_has_stories_record(self, comic_id: int, story_id: int):
        """
        Creates a new Comics_has_Stories record if the comic_id and story_id aren't already related
        :param comic_id: The unique ID of the comic resource.
        :param story_id: The unique ID of the story resource.
        """

        query = "INSERT INTO Comics_has_Stories (comicId, storyId) SELECT %s, %s WHERE NOT EXISTS " \
                "(SELECT * FROM Comics_has_Stories WHERE comicId=%s AND storyId=%s);"
        params = (comic_id, story_id, comic_id, story_id)

        try:
            print("Executing %s with %s" % (query, params))
            self.cursor.execute(query, params)
            self._commit_to_db()
        except InvalidCursorExecute:
            print(
                f"COMIC : STORY M:M RELATIONSHIP {comic_id} : {story_id} WITH NOT UPLOADED TO Comics_has_Stories TABLE"
            )
            self._connection.rollback()

    def upload_new_comics_has_variants_record(self, comic_id: int, variant_id: int):
        """
        Creates a new Comics_has_Stories record if the comic_id and story_id aren't already related
        :param comic_id: The unique ID of the comic resource.
        :param variant_id: The unique ID of the variant comic resource.
        """

        query = "INSERT INTO Comics_has_Variants (comicId, variantId) SELECT %s, %s WHERE NOT EXISTS " \
                "(SELECT * FROM Comics_has_Variants WHERE comicId=%s AND variantId=%s);"
        params = (comic_id, variant_id, comic_id, variant_id)

        try:
            print("Executing %s with %s" % (query, params))
            self.cursor.execute(query, params)
            self._commit_to_db()
        except InvalidCursorExecute:
            print(
                f"COMIC : VARIANT M:M RELATIONSHIP {comic_id} : {variant_id} WITH NOT UPLOADED TO Comics_has_Variants TABLE"
            )
            self._connection.rollback()

    ################################################################
    #  CREATOR_has
    ################################################################
    def upload_new_creators_has_stories_record(self, creator_id: int, story_id: int):
        """
        Creates a new Creators_has_Stories record if the creator_id and story_id aren't already related
        :param creator_id: The unique ID of the creator resource.
        :param story_id: The unique ID of the story resource.
        """

        query = "INSERT INTO Creators_has_Stories (creatorId, storyId) SELECT %s, %s WHERE NOT EXISTS " \
                "(SELECT * FROM Creators_has_Stories WHERE creatorId=%s AND storyId=%s);"
        params = (creator_id, story_id, creator_id, story_id)

        try:
            print("Executing %s with %s" % (query, params))
            self.cursor.execute(query, params)
            self._commit_to_db()
        except InvalidCursorExecute:
            print(
                f"CREATOR : STORY M:M RELATIONSHIP {creator_id} : {story_id} WITH NOT UPLOADED TO Creators_has_Stories TABLE"
            )
            self._connection.rollback()

    def upload_new_creators_has_events_record(self, creator_id: int, event_id: int):
        """
        Creates a new Creators_has_Stories record if the creator_id and story_id aren't already related
        :param creator_id: The unique ID of the creator resource.
        :param event_id: The unique ID of the event resource.
        """

        query = "INSERT INTO Creators_has_Events (creatorId, eventId) SELECT %s, %s WHERE NOT EXISTS " \
                "(SELECT * FROM Creators_has_Events WHERE creatorId=%s AND eventId=%s);"
        params = (creator_id, event_id, creator_id, event_id)

        try:
            print("Executing %s with %s" % (query, params))
            self.cursor.execute(query, params)
            self._commit_to_db()
        except InvalidCursorExecute:
            print(
                f"CREATOR : EVENT M:M RELATIONSHIP {creator_id} : {event_id} WITH NOT UPLOADED TO Creators_has_Events TABLE"
            )
            self._connection.rollback()

    def upload_new_creators_has_series_record(self, creator_id: int, series_id: int):
        """
        Creates a new Creators_has_Series record if the creator_id and series_id aren't already related
        :param creator_id: The unique ID of the creator resource.
        :param series_id: The unique ID of the series resource.
        """

        query = "INSERT INTO Creators_has_Series (creatorId, seriesId) SELECT %s, %s WHERE NOT EXISTS " \
                "(SELECT * FROM Creators_has_Series WHERE creatorId=%s AND seriesId=%s);"
        params = (creator_id, series_id, creator_id, series_id)

        try:
            print("Executing %s with %s" % (query, params))
            self.cursor.execute(query, params)
            self._commit_to_db()
        except InvalidCursorExecute:
            print(
                f"CREATOR : SERIES M:M RELATIONSHIP {creator_id} : {series_id} WITH NOT UPLOADED TO Creators_has_Series TABLE"
            )
            self._connection.rollback()

    def upload_new_creators_has_urls_record(self, creator_id: int, url: str):
        """
        Creates a new Creators_has_URLs record if the creator_id and url aren't already related
        :param creator_id: The unique ID of the creator resource.
        :param url: The unique url.
        """

        query = "INSERT INTO Creators_has_URLs (creatorId, url) SELECT %s, %s WHERE NOT EXISTS " \
                "(SELECT * FROM Creators_has_URLs WHERE creatorId=%s AND url=%s);"
        params = (creator_id, url, creator_id, url)

        try:
            print("Executing %s with %s" % (query, params))
            self.cursor.execute(query, params)
            self._commit_to_db()
        except InvalidCursorExecute:
            print(
                f"CREATOR : URL M:M RELATIONSHIP {creator_id} : {url} WITH NOT UPLOADED TO Creators_has_URLs TABLE"
            )
            self._connection.rollback()

    '''
    ####################################################################################################################
    #
    #                                           DELETE RECORDS
    #
    ####################################################################################################################
    '''
    def delete_from_scanned_upc_codes_table(self, upc_code: str):
        """
        Deletes records from the scanned_upc_codes table based on the upc_code provided.
        :param upc_code: full upc_code string including prefix
        """

        query = "DELETE FROM scanned_upc_codes WHERE upc_code=%s;"
        params = (upc_code,)

        try:
            print("Executing %s with %s" % (query, params))
            self.cursor.execute(query, params)
            self._commit_to_db()
        except InvalidCursorExecute:
            print(f"DELETE {upc_code} NOT DELETED FROM scanned_upc_codes TABLE")
            self._connection.rollback()

    '''
    ####################################################################################################################
    #
    #                                       DATABASE MANAGEMENT
    #
    ####################################################################################################################
    '''

    def close_cursor(self):
        """
        Closes the db connection
        """
        self.cursor.close()

    def _commit_to_db(self):
        """
        Commits changes to database
        """
        self._connection.commit()

    def _connect_to_database(self):
        """
        manages connecting to the database
        :return: the MySQLdb.connect() object
        """
        db_connection = MySQLdb.connect(self._host, self._user, self._passwd, self._db)
        if db_connection:
            print("DB CONNECTED...")
            return db_connection
        else:
            print("DB NOT CONNECTED...")
            return None
