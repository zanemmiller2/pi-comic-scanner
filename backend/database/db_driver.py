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
    CHARACTER_ENTITY = "Characters"
    COMIC_ENTITY = "Comics"
    CREATOR_ENTITY = "Creators"
    EVENT_ENTITY = "Events"
    IMAGE_ENTITY = "Images"
    SERIES_ENTITY = "Series"
    STORY_ENTITY = "Stories"
    URL_ENTITY = "URLs"
    PURCHASED_COMICS_ENTITY = 'PurchasedComics'
    ENTITIES = (CHARACTER_ENTITY, COMIC_ENTITY, CREATOR_ENTITY, EVENT_ENTITY, IMAGE_ENTITY,
                SERIES_ENTITY, STORY_ENTITY, URL_ENTITY, PURCHASED_COMICS_ENTITY)

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

        self.DB_DEBUG = False

    ####################################################################################################################
    #
    #                                       GET FROM DATABASE
    #
    ####################################################################################################################
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
            self._execute_commit(query)
        except InvalidCursorExecute:
            print(f"GET UPCS ERROR")
            self._connection.rollback()

        return self.cursor.fetchall()

    def get_stale_entity(self, entity_name: str):
        """
        Selects the Entity records that have a modified date older than a year ago or no modified date at all.
        Entities with no modified date were most likely added as a bare bones foreign key dependency.
        :return: set of entity ids to update
        """
        if entity_name in self.ENTITIES:

            query = f"SELECT id from {entity_name} " \
                    f"WHERE " \
                    f"{entity_name}.modified IS NULL OR " \
                    f"YEAR(CURRENT_TIMESTAMP) - YEAR({entity_name}.modified) > 1 LIMIT 10, 10;"

            try:
                self._execute_commit(query)
            except InvalidCursorExecute:
                print(f"GET STALE {entity_name.upper()} ERROR")
                self._connection.rollback()

            return self.cursor.fetchall()

    ####################################################################################################################
    #
    #                                       UPLOAD TO DATABASE
    #
    ####################################################################################################################

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
            self._execute_commit(query, params)
        except InvalidCursorExecute:
            print(f"UPC {params[0]} NOT UPLOADED TO BUFFER") if self.DB_DEBUG else 0
            self._connection.rollback()

    def upload_complete_comic_book(self, params: tuple):
        """
        Inserts a new comic book record in the comic_books.comics table
        :param params: a tuple of comic book column values
        """
        query = f"INSERT INTO Comics " \
                f"(id, digitalId, title, issueNumber, variantDescription, description, modified, isbn, upc, diamondCode, " \
                f"ean, issn, format, pageCount, textObjects, resourceURI, onSaleDate, focDate, unlimitedDate, " \
                f"digitalPurchaseDate, printPrice, digitalPurchasePrice, seriesId, " \
                f"thumbnail, originalIssue) " \
                f"VALUES " \
                f"(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, " \
                f"%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) " \
                f"ON DUPLICATE KEY UPDATE " \
                f"digitalId = COALESCE (%s, VALUES(digitalId)), " \
                f"title = COALESCE (%s, VALUES(title)), " \
                f"issueNumber = COALESCE (%s, VALUES(issueNumber)), " \
                f"variantDescription = COALESCE (%s, VALUES(variantDescription)), " \
                f"description = COALESCE (%s, VALUES(description)), " \
                f"modified = COALESCE (%s, VALUES(modified)), " \
                f"isbn = COALESCE (%s, VALUES(isbn)), " \
                f"upc = COALESCE (%s, VALUES(upc)), " \
                f"diamondCode = COALESCE (%s, VALUES(diamondCode)), " \
                f"ean = COALESCE (%s, VALUES(ean)), " \
                f"issn = COALESCE (%s, VALUES(issn)), " \
                f"format = COALESCE (%s, VALUES(format)), " \
                f"pageCount = COALESCE (%s, VALUES(pageCount)), " \
                f"textObjects = COALESCE (%s, VALUES(textObjects)), " \
                f"resourceURI = COALESCE (%s, VALUES(resourceURI)), " \
                f"onSaleDate = COALESCE (%s, VALUES(onSaleDate)), " \
                f"focDate = COALESCE (%s, VALUES(focDate)), " \
                f"unlimitedDate = COALESCE (%s, VALUES(unlimitedDate)), " \
                f"digitalPurchaseDate = COALESCE (%s, VALUES(digitalPurchaseDate)), " \
                f"printPrice = COALESCE (%s, VALUES(printPrice)), " \
                f"digitalPurchasePrice = COALESCE (%s, VALUES(digitalPurchasePrice)), " \
                f"seriesId = COALESCE (%s, VALUES(seriesId)), " \
                f"thumbnail = COALESCE (%s, VALUES(thumbnail)), " \
                f"originalIssue = COALESCE (%s, VALUES(originalIssue));"

        try:
            self._execute_commit(query, params)
        except InvalidCursorExecute:
            print(f"COMIC {params[0]} : {params[2]} NOT UPLOADED TO Comics TABLE") if self.DB_DEBUG else 0
            self._connection.rollback()

    def upload_complete_creator(self, params: tuple):
        """
        Updates/Inserts a Creator in the comic_books.creators table
        :param params: a tuple of creator column values
        """

        query = f"INSERT INTO Creators " \
                f"(id, firstName, middleName, lastName, suffix, modified, resourceURI, thumbnail) " \
                f"VALUES " \
                f"(%s, %s, %s, %s, %s, %s, %s, %s) " \
                f"ON DUPLICATE KEY UPDATE " \
                f"firstName = COALESCE (%s, VALUES(firstName)), " \
                f"middleName = COALESCE (%s, VALUES(middleName)), " \
                f"lastName = COALESCE (%s, VALUES(lastName)), " \
                f"suffix = COALESCE (%s, VALUES(suffix)), " \
                f"modified = COALESCE (%s, VALUES(modified)), " \
                f"resourceURI = COALESCE (%s, VALUES(resourceURI)), " \
                f"thumbnail = COALESCE (%s, VALUES(thumbnail));"

        try:
            self._execute_commit(query, params)
        except InvalidCursorExecute:
            print(f"CREATOR {params[0]} : {params[2]} NOT UPLOADED TO Comics TABLE") if self.DB_DEBUG else 0
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
                f"purchasedDate = COALESCE (%s, VALUES(purchasedDate))," \
                f"purchasePrice = COALESCE (%s, VALUES(purchasePrice))," \
                f"purchaseType = COALESCE (%s, VALUES(purchaseType));"
        try:
            self._execute_commit(query, params)
        except InvalidCursorExecute:
            print(f"PURCHASED COMIC {params[0]} NOT UPLOADED TO PurchasedComics TABLE")
            self._connection.rollback()

    def upload_complete_series(self, params: tuple):
        """
        Uploads a complete record to the Series Table
        """
        query = f"INSERT INTO Series " \
                f"(id, title, description, resourceURI, startYear, endYear, rating, modified, thumbnail, " \
                f"nextSeriesId, previousSeriesId, Series.type) " \
                f"VALUES " \
                f"(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) " \
                f"ON DUPLICATE KEY UPDATE " \
                f"title = COALESCE(%s, VALUES(title)), " \
                f"description = COALESCE(%s, VALUES(description))," \
                f"resourceURI = COALESCE(%s, VALUES(resourceURI))," \
                f"startYear = COALESCE(%s, VALUES(startYear)), " \
                f"endYear = COALESCE(%s, VALUES(endYear)), " \
                f"rating = COALESCE(%s, VALUES(rating)), " \
                f"modified = COALESCE(%s, VALUES(modified)), " \
                f"thumbnail = COALESCE(%s, VALUES(thumbnail)), " \
                f"nextSeriesId = COALESCE(%s, VALUES(nextSeriesId)), " \
                f"previousSeriesId = COALESCE(%s, VALUES(previousSeriesId))," \
                f"Series.type = COALESCE(%s, VALUES(Series.type));"
        try:
            self._execute_commit(query, params)
        except InvalidCursorExecute:
            print(f"SERIES {params[0]} NOT UPLOADED TO Series TABLE")
            self._connection.rollback()

    def upload_complete_story(self, params: tuple):
        """
        Uploads a complete record to the Stories Table
        """
        query = f"INSERT INTO Stories " \
                f"(id, title, description, resourceURI, Stories.type, modified, thumbnail) " \
                f"VALUES " \
                f"(%s, %s, %s, %s, %s, %s, %s) " \
                f"ON DUPLICATE KEY UPDATE " \
                f"title = COALESCE(%s, VALUES(title)), " \
                f"description = COALESCE(%s, VALUES(description))," \
                f"resourceURI = COALESCE(%s, VALUES(resourceURI)), " \
                f"Stories.type = COALESCE(%s, VALUES(Stories.type))," \
                f"modified = COALESCE(%s, VALUES(modified)), " \
                f"thumbnail = COALESCE(%s, VALUES(thumbnail));"
        try:
            self._execute_commit(query, params)
        except InvalidCursorExecute:
            print(f"STORY {params[0]} NOT UPLOADED TO Stories TABLE")
            self._connection.rollback()

    def upload_complete_character(self, params: tuple):
        """
        Uploads a complete record to the Characters Table
        """
        query = f"INSERT INTO Characters " \
                f"(id, Characters.name, description, modified, resourceURI, thumbnail) " \
                f"VALUES " \
                f"(%s, %s, %s, %s, %s, %s) " \
                f"ON DUPLICATE KEY UPDATE " \
                f"Characters.name = COALESCE(%s, VALUES(Characters.name)), " \
                f"description = COALESCE(%s, VALUES(description))," \
                f"modified = COALESCE(%s, VALUES(modified)), " \
                f"resourceURI = COALESCE(%s, VALUES(resourceURI)), " \
                f"thumbnail = COALESCE(%s, VALUES(thumbnail));"
        try:
            self._execute_commit(query, params)
        except InvalidCursorExecute:
            print(f"STORY {params[0]} NOT UPLOADED TO Stories TABLE")
            self._connection.rollback()

    def upload_complete_event(self, params: tuple):
        """
        Uploads a complete record to the Events Table
        """
        query = f"INSERT INTO Events " \
                f"(id, title, description, resourceURI, modified, Events.start, Events.end, " \
                f"thumbnail, nextEventId, previousEventId) " \
                f"VALUES " \
                f"(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) " \
                f"ON DUPLICATE KEY UPDATE " \
                f"title = COALESCE(%s, VALUES(title)), " \
                f"description = COALESCE(%s, VALUES(description))," \
                f"resourceURI = COALESCE(%s, VALUES(resourceURI)), " \
                f"modified = COALESCE(%s, VALUES(modified)), " \
                f"Events.start = COALESCE(%s, VALUES(Events.start)), " \
                f"Events.end = COALESCE(%s, VALUES(Events.end)), " \
                f"thumbnail = COALESCE(%s, VALUES(thumbnail)), " \
                f"nextEventId = COALESCE(%s, VALUES(nextEventId)), " \
                f"previousEventId = COALESCE(%s, VALUES(previousEventId));"
        try:
            self._execute_commit(query, params)
        except InvalidCursorExecute:
            print(f"EVENT {params[0]} NOT UPLOADED TO Events TABLE")
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

        query = "INSERT INTO Images " \
                "(Images.path, pathExtension) " \
                "VALUES " \
                "(%s, %s) " \
                "ON DUPLICATE KEY UPDATE " \
                "pathExtension = COALESCE(%s, VALUES(pathExtension));"
        params = (image_path, image_extension, image_extension)

        try:
            self._execute_commit(query, params)
        except InvalidCursorExecute:
            print(f"IMAGE {image_path + image_extension} NOT UPLOADED TO Images TABLE")
            self._connection.rollback()

    def upload_new_url_record(self, url_type: str, url_path: str):
        """
        Uploads a new url record to comic_books.URLs if URL does not already exist in database
        :param url_type: string of the url type description
        :param url_path: string of the full url to upload
        """

        query = "INSERT INTO URLs " \
                "(URLs.type, url) " \
                "VALUES " \
                "(%s, %s) " \
                "ON DUPLICATE KEY UPDATE " \
                "URLs.type = COALESCE(%s, VALUES(URLs.type));"
        params = (url_type, url_path, url_type)

        try:
            self._execute_commit(query, params)
        except InvalidCursorExecute:
            print(f"URL {url_type} : {url_path} NOT UPLOADED TO URLs TABLE")
            self._connection.rollback()

    def upload_new_creator_record(self, creator_id: int, first_name: str, middle_name: str,
                                  last_name: str, resource_uri: str):
        """
        Uploads a new creator record to comic_books.creators if Creator does not already exist in database
        :param creator_id: The unique ID of the creator resource.
        :param first_name: The first name of the creator.
        :param middle_name: The middle name of the creator.
        :param last_name: The last name of the creator.
        :param resource_uri: The canonical URL identifier for this resource.
        """

        query = "INSERT INTO Creators " \
                "(id, firstName, middleName, lastName, resourceURI) " \
                "VALUES " \
                "(%s, %s, %s, %s, %s) " \
                "ON DUPLICATE KEY UPDATE " \
                "firstName = COALESCE(%s, VALUES(firstName)), " \
                "middleName = COALESCE(%s, VALUES(middleName)), " \
                "lastName = COALESCE(%s, VALUES(lastName)), " \
                "resourceURI = COALESCE(%s, VALUES(resourceURI));"

        params = (creator_id, first_name, middle_name, last_name, resource_uri,
                  first_name, middle_name, last_name, resource_uri)

        try:
            self._execute_commit(query, params)
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

        query = "INSERT INTO Characters " \
                "(id, Characters.name, resourceURI) " \
                "VALUES " \
                "(%s, %s, %s) " \
                "ON DUPLICATE KEY UPDATE " \
                "Characters.name = COALESCE(%s, VALUES(Characters.name)), " \
                "resourceURI = COALESCE(%s, VALUES(resourceURI));"

        params = (character_id, character_name, character_uri, character_name, character_uri)

        try:
            self._execute_commit(query, params)
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

        query = "INSERT INTO Stories " \
                "(id, title, resourceURI, Stories.type) " \
                "VALUES " \
                "(%s, %s, %s, %s) " \
                "ON DUPLICATE KEY UPDATE " \
                "title = COALESCE(%s, VALUES(title)), " \
                "resourceURI = COALESCE(%s, VALUES(resourceURI)), " \
                "Stories.type = COALESCE(%s, VALUES(Stories.type));"

        params = (story_id, story_title, story_uri, story_type, story_title, story_uri, story_type)

        try:
            self._execute_commit(query, params)
        except InvalidCursorExecute:
            print(f"STORY {story_id} : {story_title} NOT UPLOADED TO Stories TABLE")
            self._connection.rollback()

    def upload_new_variants_record(self, variant_id: int, variant_title: str, variant_uri: str, issue_number: float,
                                   is_variant: bool):
        """
        Uploads a new story record to comic_books.stories if story does not already exist in database
        :param variant_id: The unique ID of the comic resource.
        :param variant_title: The variant comic title.
        :param variant_uri: The canonical URL identifier for this resource.
        :param issue_number: The issue number of the variant comic in the series
        :param is_variant: boolean value denoting if the comic is a variant
        """

        query = "INSERT INTO Comics " \
                "(id, title, resourceURI, issueNumber, isVariant) " \
                "VALUES " \
                "(%s, %s, %s, %s, %s) " \
                "ON DUPLICATE KEY UPDATE " \
                "title = COALESCE(%s, VALUES(title)), " \
                "resourceURI = COALESCE(%s, VALUES(resourceURI)), " \
                "issueNumber = COALESCE(%s, VALUES(issueNumber)), " \
                "isVariant = COALESCE(%s, VALUES(isVariant));"

        params = (variant_id, variant_title, variant_uri, issue_number, is_variant,
                  variant_title, variant_uri, issue_number, is_variant)

        try:
            self._execute_commit(query, params)
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
        query = "INSERT INTO Comics " \
                "(id, title, resourceURI) " \
                "VALUES " \
                "(%s, %s, %s) " \
                "ON DUPLICATE KEY UPDATE " \
                "title = COALESCE(%s, VALUES(title)), " \
                "resourceURI = COALESCE(%s, VALUES(resourceURI));"

        params = (comic_id, comic_title, comic_uri, comic_title, comic_uri)

        try:
            self._execute_commit(query, params)
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
            self._execute_commit(query, params)
        except InvalidCursorExecute:
            print(f"NEW RECORD {entity_id} : {entity_title} NOT UPLOADED TO {table_name} TABLE")
            self._connection.rollback()

    ####################################################################################################################
    #
    #                                       ADD NEW ENTITY_HAS_RELATIONSHIPS
    #
    ####################################################################################################################

    ################################################################
    #  COMICS_has
    ################################################################

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
            self._execute_commit(query, params)
        except InvalidCursorExecute:
            print(
                    f"COMIC : VARIANT M:M RELATIONSHIP {comic_id} : {variant_id} WITH NOT UPLOADED TO Comics_has_Variants TABLE"
            )
            self._connection.rollback()

    ################################################################
    #  ENTITY_has
    ################################################################
    def upload_new_entity_has_characters_record(self, parent_entity: str, parent_id: int, character_id: int):
        """
        Creates a new Entity_has_Characters record if the parent_id and character_id aren't already related
        :param parent_entity: the name of the parent entity
        :param parent_id: The unique ID of the parent resource.
        :param character_id: The unique ID of the character resource.
        """
        parentIdName = self.get_parent_id_name(parent_entity)

        if parentIdName is not None:
            tableName = parent_entity + '_has_' + self.CHARACTER_ENTITY

            query = f"INSERT INTO {tableName} ({parentIdName}, characterId) SELECT %s, %s WHERE NOT EXISTS " \
                    f"(SELECT * FROM {tableName} WHERE {parentIdName}=%s AND characterId=%s);"
            params = (parent_id, character_id, parent_id, character_id)

            try:
                self._execute_commit(query, params)
            except InvalidCursorExecute:
                print(
                        f"{parent_entity.upper()} : CHARACTER M:M RELATIONSHIP {parent_id} : {character_id} WITH NOT UPLOADED TO {tableName} TABLE"
                )
                self._connection.rollback()

    def upload_new_entity_has_creators_record(self, parent_entity: str, parent_id: int, creator_id: int,
                                              creator_role: str = None):
        """
        Creates a new Comics_has_Creators record if the comic_id and character_id aren't already related with the
        creator_role
        :param parent_entity: the name of the parent entity
        :param parent_id: The unique ID of the parent entity resource.
        :param creator_id: The unique ID of the creator resource.
        :param creator_role: The role of the creator in the parent entity.
        """

        parentIdName = self.get_parent_id_name(parent_entity)

        if parentIdName is not None:
            tableName = parent_entity + '_has_' + self.CREATOR_ENTITY

            query = f"INSERT INTO {tableName} " \
                    f"({parentIdName}, creatorId, creatorRole) " \
                    f"VALUES " \
                    f"(%s, %s, %s)" \
                    f"ON DUPLICATE KEY UPDATE " \
                    f"creatorRole = COALESCE (VALUES(creatorRole), %s);"
            params = (parent_id, creator_id, creator_role, creator_role)

            try:
                self._execute_commit(query, params)
            except InvalidCursorExecute:
                print(
                        f"{parent_entity.upper()} : CREATOR M:M RELATIONSHIP {parent_id} : {creator_id} WITH "
                        f"ROLE {creator_role} NOT UPLOADED TO {tableName} TABLE"
                )
                self._connection.rollback()

    def upload_new_entity_has_events_record(self, parent_entity: str, parent_id: int, event_id: int):
        """
        Creates a new Entity_has_Events record if the parent_id and event_id aren't already related
        :param parent_entity: the name of the parent entity
        :param parent_id: The unique ID of the parent resource.
        :param event_id: The unique ID of the event resource.
        """

        parentIdName = self.get_parent_id_name(parent_entity)

        if parentIdName is not None:
            tableName = parent_entity + '_has_' + self.EVENT_ENTITY
            query = f"INSERT INTO {tableName} ({parentIdName}, eventId) SELECT %s, %s WHERE NOT EXISTS " \
                    f"(SELECT * FROM {tableName} WHERE {parentIdName}=%s AND eventId=%s);"
            params = (parent_id, event_id, parent_id, event_id)

            try:
                self._execute_commit(query, params)
            except InvalidCursorExecute:
                print(
                    f"{parent_entity.upper()} : EVENTS M:M RELATIONSHIP {parent_id} : {event_id} NOT UPLOADED TO {tableName} TABLE")
                self._connection.rollback()

    def upload_new_entity_has_images_record(self, parent_entity: str, parent_id: int, image_path: str):
        """
        Creates a new parent_entity_has_Images record if the parent_id and image_path aren't already related
        :param parent_entity: the name of the parent entity
        :param parent_id: The unique ID of the parent resource.
        :param image_path: The full path of the image resource
        """
        parentIdName = self.get_parent_id_name(parent_entity)

        if parentIdName is not None:
            tableName = parent_entity + '_has_' + self.IMAGE_ENTITY

            query = f"INSERT INTO {tableName} ({parentIdName}, imagePath) " \
                    f"SELECT %s, %s WHERE NOT EXISTS " \
                    f"(SELECT * FROM {tableName} " \
                    f"WHERE " \
                    f"{parentIdName}=%s " \
                    f"AND " \
                    f"imagePath=%s);"

            params = (parent_id, image_path, parent_id, image_path)

            try:
                self._execute_commit(query, params)
            except InvalidCursorExecute:
                print(f"{parent_entity.upper()} : IMAGE M:M RELATIONSHIP {parent_id} : {image_path} NOT UPLOADED TO "
                      f"{tableName} TABLE")
                self._connection.rollback()

    def upload_new_entity_has_stories_record(self, parent_entity: str, parent_id: int, story_id: int):
        """
        Creates a new Entity_has_Stories record if the parent_id and story_id aren't already related
        :param parent_entity: the name of the parent entity
        :param parent_id: The unique ID of the parent resource.
        :param story_id: The unique ID of the parent resource.
        """

        parentIdName = self.get_parent_id_name(parent_entity)
        if parentIdName is not None:
            tableName = parent_entity + '_has_' + self.STORY_ENTITY
            query = f"INSERT INTO {tableName} ({parentIdName}, storyId) SELECT %s, %s WHERE NOT EXISTS " \
                    f"(SELECT * FROM {tableName} WHERE {parentIdName}=%s AND storyId=%s);"
            params = (parent_id, story_id, parent_id, story_id)

            try:
                self._execute_commit(query, params)
            except InvalidCursorExecute:
                print(
                        f"{parent_entity.upper()} : STORY M:M RELATIONSHIP {parent_id} : {story_id} NOT UPLOADED TO {tableName} TABLE"
                )
                self._connection.rollback()

    def upload_new_entity_has_urls_record(self, parent_entity: str, parent_id: int, url: str):
        """
        Creates a new Entity_has_Stories record if the comic_id and story_id aren't already related
        :param parent_entity: the name of the parent entity
        :param parent_id: The unique ID of the parent resource.
        :param url: A full URL (including scheme, domain, and path) related to the entity.
        """
        parentIdName = self.get_parent_id_name(parent_entity)
        if parentIdName is not None:
            tableName = parent_entity + '_has_' + self.URL_ENTITY
            query = f"INSERT INTO {tableName} ({parentIdName}, url) SELECT %s, %s WHERE NOT EXISTS " \
                    f"(SELECT * FROM {tableName} WHERE {parentIdName}=%s AND url=%s);"
            params = (parent_id, url, parent_id, url)

            try:
                self._execute_commit(query, params)
            except InvalidCursorExecute:
                print(
                        f"{parent_entity.upper()} : URL M:M RELATIONSHIP {parent_id} : {url} WITH NOT UPLOADED TO {tableName} TABLE")
                self._connection.rollback()

    ####################################################################################################################
    #
    #                                           DELETE RECORDS
    #
    ####################################################################################################################
    def delete_from_scanned_upc_codes_table(self, upc_code: str):
        """
        Deletes records from the scanned_upc_codes table based on the upc_code provided.
        :param upc_code: full upc_code string including prefix
        """

        query = "DELETE FROM scanned_upc_codes WHERE upc_code=%s;"
        params = (upc_code,)

        try:
            self._execute_commit(query, params)
        except InvalidCursorExecute:
            print(f"DELETE {upc_code} NOT DELETED FROM scanned_upc_codes TABLE")
            self._connection.rollback()

    ####################################################################################################################
    #
    #                                   UTILITIES
    #
    ####################################################################################################################
    def get_parent_id_name(self, parent_entity):
        if parent_entity == self.CHARACTER_ENTITY:
            return "characterId"
        elif parent_entity == self.COMIC_ENTITY:
            return "comicId"
        elif parent_entity == self.CREATOR_ENTITY:
            return "creatorId"
        elif parent_entity == self.EVENT_ENTITY:
            return "eventId"
        elif parent_entity == self.SERIES_ENTITY:
            return "seriesId"
        elif parent_entity == self.STORY_ENTITY:
            return "storyId"
        else:
            print(f"{parent_entity} HAS NO CREATOR RELATION... ") if self.DB_DEBUG else 0
            return None

    ####################################################################################################################
    #
    #                                       DATABASE MANAGEMENT
    #
    ####################################################################################################################
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

    def _execute_commit(self, query, params=None):
        if params is None:
            print("Executing %s", query) if self.DB_DEBUG else 0
            self.cursor.execute(query)
        else:
            print("Executing %s with %s" % (query, params)) if self.DB_DEBUG else 0
            self.cursor.execute(query, params)

        self._commit_to_db()
