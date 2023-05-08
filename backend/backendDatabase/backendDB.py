"""
Author: Zane Miller
Email: millerzanem@gmail.com
Date: 04/21/2023
Description: Class drivers for backendDatabase functions
"""
from __future__ import annotations

import MySQLdb
from keys import db_credentials


class InvalidCursorExecute(Exception):
    """ cursor.execute failed """
    pass


class BackEndDB:
    """
    BackEndDB Object that represents a connection and cursor for the provided backendDatabase and credentials
    """
    CHARACTER_ENTITY = "Characters"
    COMIC_ENTITY = "Comics"
    CREATOR_ENTITY = "Creators"
    EVENT_ENTITY = "Events"
    IMAGE_ENTITY = "Images"
    SERIES_ENTITY = "Series"
    STORY_ENTITY = "Stories"
    URL_ENTITY = "URLs"
    VARIANT_ENTITY = "Variants"
    PREVIOUS_SERIES_ENTITY = "PreviousSeries"
    NEXT_SERIES_ENTITY = "NextSeries"
    PURCHASED_COMICS_ENTITY = 'PurchasedComics'
    ENTITIES = (CHARACTER_ENTITY, COMIC_ENTITY, CREATOR_ENTITY, EVENT_ENTITY, IMAGE_ENTITY,
                SERIES_ENTITY, STORY_ENTITY, URL_ENTITY, PURCHASED_COMICS_ENTITY)

    def __init__(self):
        """
        Represents a BackEndDB object with username, hostname, password, backendDatabase name, cursor, and connection
        """
        # self._host = input("BackEndDB Host: ")
        # self._user = input("BackEndDB User: ")
        # self._passwd = input("BackEndDB Password: ")
        # self._db_name = input("BackEndDB Name: ")

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
        Selects all entries from scanned_upc_codes from comic_books backendDatabase
        :return: db cursor
        """
        if self._connection is None:
            print(
                "No connection to the backendDatabase found! Have you called connect_to_database() first?"
            )
            return None

        query = "SELECT upc_code, date_uploaded FROM scanned_upc_codes;"

        try:
            self._execute_commit(query)
            return self.cursor.fetchall()
        except InvalidCursorExecute:
            print(f"GET UPCS ERROR")
            self._connection.rollback()

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
                    f"YEAR(CURRENT_TIMESTAMP) - YEAR({entity_name}.modified) > 1 LIMIT 55, 5;"

            try:
                self._execute_commit(query)
                return self.cursor.fetchall()
            except InvalidCursorExecute:
                print(f"GET STALE {entity_name.upper()} ERROR")
                self._connection.rollback()

    def get_comic_purchased_ids(self):
        """
        Gets a list of all purchased comic ids
        :return: list of purchased comic ids
        """

        query = "SELECT comicId FROM PurchasedComics;"
        try:
            self._execute_commit(query)
            return self.cursor.fetchall()
        except InvalidCursorExecute:
            print(f"GET PURCHASED COMIC IDS FROM PurchasedComics ERROR")
            self._connection.rollback()

    def get_comic_has_entity_ids(self, entity: str, comic_id: int):
        """
        Get the entity Ids related to the given comic
        :param entity: the name of the dependent entity
        :param comic_id: the id of the related comic
        :return: the entity ids
        """
        entity_id_name = self.get_parent_id_name(entity)

        if entity == self.SERIES_ENTITY:
            table_name = 'Comics'
            comic_id_name = 'id'
        else:
            table_name = f"Comics_has_{entity}"
            comic_id_name = 'comicId'

        query = f"SELECT {entity_id_name} " \
                f"FROM {table_name} " \
                f"WHERE {comic_id_name}=%s;"
        params = (comic_id,)

        try:
            self._execute_commit(query, params)
            return self.cursor.fetchall()
        except InvalidCursorExecute:
            print(f"GET {entity} IDS FROM {table_name} ERROR WITH COMIC ID: {comic_id}")
            self._connection.rollback()

    def get_series_has_entity_ids(self, entity: str, series_id: int):
        """
        Get the entity Ids related to the given comic
        :param entity: the name of the dependent entity
        :param series_id: the id of the related series
        :return: the entity ids
        """
        entity_id_name = self.get_parent_id_name(entity)

        if entity == self.PREVIOUS_SERIES_ENTITY or entity == self.NEXT_SERIES_ENTITY:
            table_name = 'Series'
            series_id_name = 'id'
        elif entity == self.COMIC_ENTITY:
            table_name = 'Comics'
            series_id_name = 'seriesId'
            entity_id_name = 'id as comicId'
        else:
            table_name = f"Series_has_{entity}"
            series_id_name = 'seriesId'

        query = f"SELECT {entity_id_name} " \
                f"FROM {table_name} " \
                f"WHERE {series_id_name}=%s;"
        params = (series_id,)

        try:
            self._execute_commit(query, params)
            return self.cursor.fetchall()
        except InvalidCursorExecute:
            print(f"GET {entity} IDS FROM {table_name} ERROR WITH SERIES ID: {series_id}")
            self._connection.rollback()

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
        Uploads a tuple of strings (upc and YYYY-MM-DD) to the scanned_upc_codes table in the comic_books backendDatabase
        :param params: (upc: str, YYYY-MM-DD: str)
        :return: cursor object from connection
        """

        query = "INSERT INTO comic_books.scanned_upc_codes(upc_code, date_uploaded, updated) VALUES (%s, %s, CURRENT_TIMESTAMP);"

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
                f"thumbnail, originalIssue, isVariant, updated) " \
                f"VALUES " \
                f"(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, " \
                f"%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP) " \
                f"ON DUPLICATE KEY UPDATE " \
                f"digitalId = COALESCE (VALUES(digitalId), digitalId), " \
                f"title = COALESCE (VALUES(title), title), " \
                f"issueNumber = COALESCE (VALUES(issueNumber), issueNumber), " \
                f"variantDescription = COALESCE (VALUES(variantDescription), variantDescription), " \
                f"description = COALESCE (VALUES(description), description), " \
                f"modified = COALESCE (VALUES(modified), modified), " \
                f"isbn = COALESCE (VALUES(isbn), isbn), " \
                f"upc = COALESCE (VALUES(upc), upc), " \
                f"diamondCode = COALESCE (VALUES(diamondCode), diamondCode), " \
                f"ean = COALESCE (VALUES(ean), ean), " \
                f"issn = COALESCE (VALUES(issn), issn), " \
                f"format = COALESCE (VALUES(format), format), " \
                f"pageCount = COALESCE (VALUES(pageCount), pageCount), " \
                f"textObjects = COALESCE (VALUES(textObjects), textObjects), " \
                f"resourceURI = COALESCE (VALUES(resourceURI), resourceURI), " \
                f"onSaleDate = COALESCE (VALUES(onSaleDate), onSaleDate), " \
                f"focDate = COALESCE (VALUES(focDate), focDate), " \
                f"unlimitedDate = COALESCE (VALUES(unlimitedDate), unlimitedDate), " \
                f"digitalPurchaseDate = COALESCE (VALUES(digitalPurchaseDate), digitalPurchaseDate), " \
                f"printPrice = COALESCE (VALUES(printPrice), printPrice), " \
                f"digitalPurchasePrice = COALESCE (VALUES(digitalPurchasePrice), digitalPurchasePrice), " \
                f"seriesId = COALESCE (VALUES(seriesId), seriesId), " \
                f"thumbnail = COALESCE (VALUES(thumbnail), thumbnail), " \
                f"originalIssue = COALESCE (VALUES(originalIssue), originalIssue), " \
                f"isVariant = COALESCE (VALUES(isVariant), isVariant), " \
                f"updated = CURRENT_TIMESTAMP;"

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
                f"(id, firstName, middleName, lastName, suffix, modified, resourceURI, thumbnail, updated) " \
                f"VALUES " \
                f"(%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP) " \
                f"ON DUPLICATE KEY UPDATE " \
                f"firstName = COALESCE (VALUES(firstName), firstName), " \
                f"middleName = COALESCE (VALUES(middleName), middleName), " \
                f"lastName = COALESCE (VALUES(lastName), lastName), " \
                f"suffix = COALESCE (VALUES(suffix), suffix), " \
                f"modified = COALESCE (VALUES(modified), modified), " \
                f"resourceURI = COALESCE (VALUES(resourceURI), resourceURI), " \
                f"thumbnail = COALESCE (VALUES(thumbnail), thumbnail), " \
                f"updated = CURRENT_TIMESTAMP;"

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
                f"(comicId, purchaseDate, purchasePrice, purchaseType, updated) " \
                f"VALUES " \
                f"(%s, %s, %s, %s, CURRENT_TIMESTAMP) " \
                f"ON DUPLICATE KEY UPDATE " \
                f"purchaseDate = COALESCE (VALUES(purchaseDate), purchaseDate)," \
                f"purchasePrice = COALESCE (VALUES(purchasePrice), purchasePrice)," \
                f"purchaseType = COALESCE (VALUES(purchaseType), purchaseType), " \
                f"updated = CURRENT_TIMESTAMP;"
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
                f"nextSeriesId, previousSeriesId, Series.type, updated) " \
                f"VALUES " \
                f"(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP) " \
                f"ON DUPLICATE KEY UPDATE " \
                f"title = COALESCE(VALUES(title), title), " \
                f"description = COALESCE(VALUES(description), description)," \
                f"resourceURI = COALESCE(VALUES(resourceURI), resourceURI)," \
                f"startYear = COALESCE(VALUES(startYear), startYear), " \
                f"endYear = COALESCE(VALUES(endYear), endYear), " \
                f"rating = COALESCE(VALUES(rating), rating), " \
                f"modified = COALESCE(VALUES(modified), modified), " \
                f"thumbnail = COALESCE(VALUES(thumbnail), thumbnail), " \
                f"nextSeriesId = COALESCE(VALUES(nextSeriesId), nextSeriesId), " \
                f"previousSeriesId = COALESCE(VALUES(previousSeriesId), previousSeriesId)," \
                f"Series.type = COALESCE(VALUES(Series.type), Series.type), " \
                f"updated = CURRENT_TIMESTAMP;"
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
                f"(id, title, description, resourceURI, Stories.type, modified, thumbnail, updated) " \
                f"VALUES " \
                f"(%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP) " \
                f"ON DUPLICATE KEY UPDATE " \
                f"title = COALESCE(VALUES(title), title), " \
                f"description = COALESCE(VALUES(description), description)," \
                f"resourceURI = COALESCE(VALUES(resourceURI), resourceURI), " \
                f"Stories.type = COALESCE(VALUES(Stories.type), Stories.type)," \
                f"modified = COALESCE(VALUES(modified), modified), " \
                f"thumbnail = COALESCE(VALUES(thumbnail), thumbnail), " \
                f"updated = CURRENT_TIMESTAMP;"
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
                f"(id, Characters.name, description, modified, resourceURI, thumbnail, updated) " \
                f"VALUES " \
                f"(%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP) " \
                f"ON DUPLICATE KEY UPDATE " \
                f"Characters.name = COALESCE(VALUES(Characters.name), Characters.name), " \
                f"description = COALESCE(VALUES(description), description)," \
                f"modified = COALESCE(VALUES(modified), modified), " \
                f"resourceURI = COALESCE(VALUES(resourceURI), resourceURI), " \
                f"thumbnail = COALESCE(VALUES(thumbnail), thumbnail), " \
                f"updated = CURRENT_TIMESTAMP;"
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
                f"thumbnail, nextEventId, previousEventId, updated) " \
                f"VALUES " \
                f"(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP) " \
                f"ON DUPLICATE KEY UPDATE " \
                f"title = COALESCE(VALUES(title), title), " \
                f"description = COALESCE(VALUES(description), description)," \
                f"resourceURI = COALESCE(VALUES(resourceURI), resourceURI), " \
                f"modified = COALESCE(VALUES(modified), modified), " \
                f"Events.start = COALESCE(VALUES(Events.start), Events.start), " \
                f"Events.end = COALESCE(VALUES(Events.end), Events.end), " \
                f"thumbnail = COALESCE(VALUES(thumbnail), thumbnail), " \
                f"nextEventId = COALESCE(VALUES(nextEventId), nextEventId), " \
                f"previousEventId = COALESCE(VALUES(previousEventId), previousEventId), " \
                f"updated = CURRENT_TIMESTAMP;"
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
        Uploads a new image path to comic_books.image_paths if image path does not already exist in backendDatabase
        :param image_path: string of the full image path to upload
        :param image_extension: extension for the image path
        """

        query = "INSERT INTO Images " \
                "(Images.path, pathExtension, updated) " \
                "VALUES " \
                "(%s, %s, CURRENT_TIMESTAMP) " \
                "ON DUPLICATE KEY UPDATE " \
                "pathExtension = COALESCE(VALUES(pathExtension), pathExtension), " \
                "updated = CURRENT_TIMESTAMP;"
        params = (image_path, image_extension)

        try:
            self._execute_commit(query, params)
        except InvalidCursorExecute:
            print(f"IMAGE {image_path + image_extension} NOT UPLOADED TO Images TABLE")
            self._connection.rollback()

    def upload_new_url_record(self, url_type: str, url_path: str):
        """
        Uploads a new url record to comic_books.URLs if URL does not already exist in backendDatabase
        :param url_type: string of the url type description
        :param url_path: string of the full url to upload
        """

        query = "INSERT INTO URLs " \
                "(URLs.type, url, updated) " \
                "VALUES " \
                "(%s, %s, CURRENT_TIMESTAMP) " \
                "ON DUPLICATE KEY UPDATE " \
                "URLs.type = COALESCE(VALUES(URLs.type), URLs.type), " \
                "updated = CURRENT_TIMESTAMP;"
        params = (url_type, url_path)

        try:
            self._execute_commit(query, params)
        except InvalidCursorExecute:
            print(f"URL {url_type} : {url_path} NOT UPLOADED TO URLs TABLE")
            self._connection.rollback()

    def upload_new_creator_record(self, creator_id: int, first_name: str, middle_name: str,
                                  last_name: str, resource_uri: str):
        """
        Uploads a new creator record to comic_books.creators if Creator does not already exist in backendDatabase
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
                "firstName = COALESCE(VALUES(firstName), firstName), " \
                "middleName = COALESCE(VALUES(middleName), middleName), " \
                "lastName = COALESCE(VALUES(lastName), lastName), " \
                "resourceURI = COALESCE(VALUES(resourceURI), resourceURI);"

        params = (creator_id, first_name, middle_name, last_name, resource_uri)

        try:
            self._execute_commit(query, params)
        except InvalidCursorExecute:
            print(f"CREATOR {creator_id} - {first_name + middle_name + last_name} NOT UPLOADED TO Creators TABLE")
            self._connection.rollback()

    def upload_new_character_record(self, character_id: int, character_name: str, character_uri: str):
        """
        Uploads a new character record to comic_books.characters if URL does not already exist in backendDatabase
        :param character_id: The unique ID of the character resource.
        :param character_name: The name of the character.
        :param character_uri: The canonical URL identifier for this resource.
        """

        query = "INSERT INTO Characters " \
                "(id, Characters.name, resourceURI) " \
                "VALUES " \
                "(%s, %s, %s) " \
                "ON DUPLICATE KEY UPDATE " \
                "Characters.name = COALESCE(VALUES(Characters.name), Characters.name), " \
                "resourceURI = COALESCE(VALUES(resourceURI), resourceURI);"

        params = (character_id, character_name, character_uri)

        try:
            self._execute_commit(query, params)
        except InvalidCursorExecute:
            print(f"CHARACTER {character_id} - {character_name} NOT UPLOADED TO Characters TABLE")
            self._connection.rollback()

    def upload_new_story_record(self, story_id: int, story_title: str, story_uri: str, story_type: str):
        """
        Uploads a new story record to comic_books.stories if story does not already exist in backendDatabase
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
                "title = COALESCE(VALUES(title), title), " \
                "resourceURI = COALESCE(VALUES(resourceURI), resourceURI), " \
                "Stories.type = COALESCE(VALUES(Stories.type), Stories.type);"

        params = (story_id, story_title, story_uri, story_type)

        try:
            self._execute_commit(query, params)
        except InvalidCursorExecute:
            print(f"STORY {story_id} : {story_title} NOT UPLOADED TO Stories TABLE")
            self._connection.rollback()

    def upload_new_variants_record(self, variant_id: int, variant_title: str, variant_uri: str, issue_number: float,
                                   is_variant: bool):
        """
        Uploads a new story record to comic_books.stories if story does not already exist in backendDatabase
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
                "title = COALESCE(VALUES(title), title), " \
                "resourceURI = COALESCE(VALUES(resourceURI), resourceURI), " \
                "issueNumber = COALESCE(VALUES(issueNumber), issueNumber), " \
                "isVariant = COALESCE(VALUES(isVariant), isVariant);"

        params = (variant_id, variant_title, variant_uri, issue_number, is_variant)

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
                "title = COALESCE(VALUES(title), title), " \
                "resourceURI = COALESCE(VALUES(resourceURI), resourceURI);"

        params = (comic_id, comic_title, comic_uri)

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
        if record does not already exist in backendDatabase using id, title, and uri
        :param table_name: the name of the table in the comic_books backendDatabase
        :param entity_id: The unique ID of the resource.
        :param entity_title: The title of the entity.
        :param entity_uri: The canonical URL identifier for this resource.
        """

        query = f"INSERT INTO {table_name} " \
                f"(id, title, resourceURI) " \
                f"VALUES (%s, %s, %s) " \
                f"ON DUPLICATE KEY UPDATE " \
                f"title = COALESCE(VALUES(title), title), " \
                f"resourceURI = COALESCE(VALUES(resourceURI), resourceURI);"

        params = (entity_id, entity_title, entity_uri)

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
        query = "INSERT INTO Comics_has_Variants (comicId, variantId, updated) " \
                "VALUES (%s, %s, CURRENT_TIMESTAMP) " \
                "ON DUPLICATE KEY UPDATE " \
                "updated = CURRENT_TIMESTAMP;"

        params = (comic_id, variant_id)

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

            query = f"INSERT INTO {tableName} " \
                    f"({parentIdName}, characterId, updated) " \
                    f"VALUES (%s, %s, CURRENT_TIMESTAMP) " \
                    f"ON DUPLICATE KEY UPDATE " \
                    f"updated = CURRENT_TIMESTAMP;"

            params = (parent_id, character_id)

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
                    f"({parentIdName}, creatorId, creatorRole, updated) " \
                    f"VALUES " \
                    f"(%s, %s, %s, CURRENT_TIMESTAMP)" \
                    f"ON DUPLICATE KEY UPDATE " \
                    f"creatorRole = COALESCE (VALUES(creatorRole), creatorRole), " \
                    f"updated = CURRENT_TIMESTAMP;"
            params = (parent_id, creator_id, creator_role)

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

            query = f"INSERT INTO {tableName} " \
                    f"({parentIdName}, eventId, updated) " \
                    f"VALUES (%s, %s, CURRENT_TIMESTAMP) " \
                    f"ON DUPLICATE KEY UPDATE " \
                    f"updated = CURRENT_TIMESTAMP;"

            params = (parent_id, event_id)

            try:
                self._execute_commit(query, params)
            except InvalidCursorExecute:
                print(
                    f"{parent_entity.upper()} : EVENTS M:M RELATIONSHIP {parent_id} : {event_id} NOT UPLOADED TO {tableName} TABLE"
                )
                self._connection.rollback()

    def upload_new_entity_has_images_record(self, parent_entity: str, parent_id: int, image_path: str):
        """
        Creates a new parent_entity_has_Images record if the parent_id and image_path aren't already related
        :param parent_entity: the name of the parent entity
        :param parent_id: The unique ID of the parent resource.
        :param image_path: The full path of the image resource
        """
        # comics only entity with has_Images yet
        if parent_entity == self.COMIC_ENTITY:
            parentIdName = self.get_parent_id_name(parent_entity)

            if parentIdName is not None:
                tableName = f"{parent_entity}_has_{self.IMAGE_ENTITY}"

                query = f"INSERT INTO {tableName} " \
                        f"({parentIdName}, imagePath, updated) " \
                        f"VALUES (%s, %s, CURRENT_TIMESTAMP) " \
                        f"ON DUPLICATE KEY UPDATE " \
                        f"updated = CURRENT_TIMESTAMP;"

                params = (parent_id, image_path)

                try:
                    self._execute_commit(query, params)
                except InvalidCursorExecute:
                    print(
                        f"{parent_entity.upper()} : IMAGE M:M RELATIONSHIP {parent_id} : {image_path} NOT UPLOADED TO "
                        f"{tableName} TABLE"
                        )
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
            tableName = f"{parent_entity}_has_{self.STORY_ENTITY}"

            query = f"INSERT INTO {tableName} " \
                    f"({parentIdName}, storyId, updated) " \
                    f"VALUES (%s, %s, CURRENT_TIMESTAMP) " \
                    f"ON DUPLICATE KEY UPDATE " \
                    f"updated = CURRENT_TIMESTAMP;"

            params = (parent_id, story_id)

            try:
                self._execute_commit(query, params)
            except InvalidCursorExecute:
                print(
                    f"{parent_entity.upper()} : STORY M:M RELATIONSHIP {parent_id} : {story_id} "
                    f"NOT UPLOADED TO {tableName} TABLE"
                    )
                self._connection.rollback()

    def upload_new_entity_has_urls_record(self, parent_entity: str, parent_id: int, url: str):
        """
        Creates a new Entity_has_Stories record if the comic_id and story_id aren't already related
        :param parent_entity: the name of the parent entity
        :param parent_id: The unique ID of the parent resource.
        :param url: A full URL (including scheme, domain, and path) related to the entity.
        """

        if (parent_entity == self.SERIES_ENTITY
                or parent_entity == self.COMIC_ENTITY
                or parent_entity == self.EVENT_ENTITY
                or parent_entity == self.CREATOR_ENTITY):

            parentIdName = self.get_parent_id_name(parent_entity)
            if parentIdName is not None:
                tableName = parent_entity + '_has_' + self.URL_ENTITY

                query = f"INSERT INTO {tableName} " \
                        f"({parentIdName}, url, updated) " \
                        f"VALUES (%s, %s, CURRENT_TIMESTAMP) " \
                        f"ON DUPLICATE KEY UPDATE " \
                        f"updated = CURRENT_TIMESTAMP;"

                params = (parent_id, url)

                try:
                    self._execute_commit(query, params)
                except InvalidCursorExecute:
                    print(
                        f"{parent_entity.upper()} : URL M:M RELATIONSHIP {parent_id} : {url} "
                        f"NOT UPLOADED TO {tableName} TABLE"
                        )
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

    def delete_from_purchased_comics(self, comic_id: int):
        query = "DELETE FROM PurchasedComics WHERE comicId=%s;"
        params = (comic_id,)

        try:
            self._execute_commit(query, params)
        except InvalidCursorExecute:
            print(f"DELETE {comic_id} NOT DELETED FROM PurchasedComics TABLE")
            self._connection.rollback()

    ####################################################################################################################
    #
    #                                   UTILITIES
    #
    ####################################################################################################################
    def get_parent_id_name(self, parent_entity) -> str | None:
        """
        Gets the id name in the Entity_has_relation table
        :param parent_entity: the name of the entity for which to return the id name
        :return: string or none if no entity not valid
        """
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
        elif parent_entity == self.VARIANT_ENTITY:
            return "variantId"
        elif parent_entity == self.PREVIOUS_SERIES_ENTITY:
            return "previousSeriesId"
        elif parent_entity == self.NEXT_SERIES_ENTITY:
            return 'nextSeriesId'
        else:
            print(f"{parent_entity} HAS NO RELATION... ") if self.DB_DEBUG else 0
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
        Commits changes to backendDatabase
        """
        self._connection.commit()

    def _connect_to_database(self):
        """
        manages connecting to the backendDatabase
        :return: the MySQLdb.connect() object
        """
        db_connection = MySQLdb.connect(self._host, self._user, self._passwd, self._db)
        if db_connection:
            print("BackEndDB CONNECTED...")
            return db_connection
        else:
            print("BackEndDB NOT CONNECTED...")
            return None

    def _execute_commit(self, query, params=None):
        if params is None:
            print("Executing %s", query) if self.DB_DEBUG else 0
            self.cursor.execute(query)
        else:
            print("Executing %s with %s" % (query, params)) if self.DB_DEBUG else 0
            self.cursor.execute(query, params)

        self._commit_to_db()
