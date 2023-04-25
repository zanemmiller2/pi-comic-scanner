"""
Author: Zane Miller
Email: millerzanem@gmail.com
Date: 04/17/2023
Description: Class drivers for looking up marvel comics with marvel public api
"""

import json

from backend.models.Entity import Entity


class ComicBook(Entity):
    """
    ComicBook object is a map of the marvel public api /comics endpoint response model. The ComicBook object is
    responsible for parsing the response data, creating new database records for specific entities and creating a new
    Comic in the database.
    """

    def __init__(
            self, db_connection, response_data, is_purchased_date: str = None, is_purchased_price: float = None,
            is_purchased_type: str = None, is_purchased: bool = False
    ):
        """ Represents a Comic book based on the marvel comic developer api json response model """
        super().__init__(db_connection, response_data)
        self.count = None  # int, optional
        self.digitalId = None  # int, optional
        self.issueNumber = None  # double, optional
        self.variantDescription = None  # string, optional
        self.isbn = None  # string, optional
        self.upc = None  # string, optional
        self.diamondCode = None  # string, optional
        self.ean = None  # string, optional
        self.issn = None  # string, optional
        self.format = None  # string, optional
        self.pageCount = None  # int, optional
        self.textObjects = {}  # Array[TextObject], optional
        # self.textObjects[type] = {
        #     'language': string, optional,
        #     'text': string, optional
        # }
        self.seriesId = None
        self.onSaleDate = None
        self.focDate = None
        self.unlimitedDate = None
        self.digitalPurchaseDate = None
        self.printPrice = None
        self.digitalPurchasePrice = None
        self.variantDetail = {}  # (variantDetail[variant_id] = {title: '', uri: ''})

        self.isPurchased = is_purchased
        if self.isPurchased is True:
            self.isPurchasedDate = self.convert_to_SQL_date(is_purchased_date)
            self.isPurchasedPrice = is_purchased_price
            self.isPurchasedType = is_purchased_type.title()

        self.ENTITY_NAME = self.COMIC_ENTITY

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
            # Unique to ComicBook() class
            self._save_dates()
            self._save_diamondCode()
            self._save_digitalId()
            self._save_ean()
            self._save_format()
            self._save_images()
            self._save_isbn()
            self._save_issn()
            self._save_issueNumber()
            self._save_pageCount()
            self._save_prices()
            self._save_textObjects()
            self._save_upc()
            self._save_variantDescription()
            self._save_variants()

            # From Parent class
            self._save_characters()
            self._save_creators()
            self._save_description()
            self._save_events()
            self._save_id()
            self._save_modified()
            self._save_originalIssueId()
            self._save_resourceURI()
            self._save_series()
            self._save_stories()
            self._save_thumbnail()
            self._save_title()
            self._save_urls()

    def upload_new_records(self):
        """
        Uploads new records to the database before uploading the entire comic book with relevant foreign keys
        """
        # Unique to ComicBook() class
        self._add_new_variant()

        # From parent class
        self._add_new_creator()
        self._add_new_character()
        self._add_new_event()
        self._add_new_image()
        self._add_new_series()
        self._add_new_story()
        self._add_new_url()

    def upload_comic_book(self):
        """
        Compiles the comic_book entities into params tuple to pass to database function for uploading complete comic
        book
        """

        params = (self.id, self.digitalId, self.title, self.issueNumber, self.variantDescription, self.description,
                  self.modified, self.isbn, self.upc, self.diamondCode, self.ean, self.issn, self.format,
                  self.pageCount, json.dumps(self.textObjects), self.resourceURI, self.onSaleDate, self.focDate,
                  self.unlimitedDate, self.digitalPurchaseDate, self.printPrice, self.digitalPurchasePrice,
                  self.seriesId, self.thumbnail, self.originalIssueId, self.digitalId,
                  self.title, self.issueNumber, self.variantDescription, self.description, self.modified, self.isbn,
                  self.upc, self.diamondCode,self.ean, self.issn, self.format, self.pageCount,
                  json.dumps(self.textObjects), self.resourceURI, self.onSaleDate, self.focDate, self.unlimitedDate,
                  self.digitalPurchaseDate, self.printPrice, self.digitalPurchasePrice, self.seriesId, self.thumbnail,
                  self.originalIssueId)

        self.db.upload_complete_comic_book(params)

    def upload_comics_has_relationships(self):
        """
        Runs through and creates all the comics_has_relationships
        """
        self._comics_has_variants()

        self._entity_has_characters()
        self._entity_has_creators()
        self._entity_has_events()
        self._entity_has_stories()
        self._entity_has_urls()
        self._entity_has_images()


        if self.isPurchased is True:
            self._upload_purchasedComic()

    def _upload_purchasedComic(self):
        """ Uploads a purchased comic to the PurchasedComics table """

        params = (self.id, self.isPurchasedDate, self.isPurchasedPrice, self.isPurchasedType, self.isPurchasedDate,
                  self.isPurchasedPrice, self.isPurchasedType)
        self.db.upload_complete_purchased_comic(params)

    ####################################################################################################################
    #
    #          ADD NEW JSON RESPONSE DATA TO CLASS VARIABLES
    #
    ####################################################################################################################

    def _save_dates(self):
        """
        A list of key dates for this comic.
        """
        for date in self.data['dates']:
            if date['type'] == "onsaleDate":
                self.onSaleDate = self.convert_to_SQL_date(date['date'])
            elif date['type'] == "focDate":
                self.focDate = self.convert_to_SQL_date(date['date'])
            elif date['type'] == "unlimitedDate":
                self.unlimitedDate = self.convert_to_SQL_date(date['date'])
            elif date['type'] == "digitalPurchaseDate":
                self.digitalPurchaseDate = self.convert_to_SQL_date(date['date'])
            else:
                print(f"{date['type']} DATE TYPE NOT CATEGORIZED")

    def _save_diamondCode(self):
        """
        The Diamond Code for the comic.
        """
        self.diamondCode = str(self.data['diamondCode'])

    def _save_digitalId(self):
        """
        The ID of the digital comic representation of this comic.
        Will be 0 if the comic is not available digitally.
        """
        self.digitalId = int(self.data['digitalId'])

    def _save_ean(self):
        """
        The EAN barcode for the comic.
        """
        self.ean = str(self.data['ean'])

    def _save_format(self):
        """
        The publication format of the comic e.g. comic, hardcover, trade paperback.
        """
        self.format = str(self.data['format'])

    def _save_images(self):
        """
        A list of promotional image_paths associated with this comic.
        """

        for image in self.data['images']:
            image_path = image['path']
            image_extension = '.' + image['extension']

            if image_path not in self.image_paths:
                self.image_paths.add((image_path, image_extension))

    def _save_isbn(self):
        """
        The ISBN for the comic (generally only populated for collection formats).
        """
        self.isbn = str(self.data['isbn'])

    def _save_issn(self):
        """
        The ISSN barcode for the comic.
        """
        self.issn = str(self.data['issn'])

    def _save_issueNumber(self):
        """
        The number of the issue in the series (will generally be 0 for collection formats).
        """
        self.issueNumber = float(self.data['issueNumber'])

    def _save_pageCount(self):
        """
        The number of story pages in the comic.
        """
        self.pageCount = int(self.data['pageCount'])

    def _save_prices(self):
        """
        A list of prices for this comic.
        """

        for price in self.data['prices']:
            if price['type'] == 'printPrice':
                self.printPrice = float(price['price'])
            elif price['type'] == 'digitalPurchasePrice':
                self.digitalPurchasePrice = float(price['price'])
            else:
                print(f"{price['type']} PRICE TYPE NOT CATEGORIZED")

    def _save_series(self):
        """
        A summary representation of the series to which this comic belongs.
        """
        if 'series' in self.data and self.data['series']:
            series_uri = self.data['series']['resourceURI']
            series_title = self.data['series']['name']
            series_id = self.get_id_from_resourceURI(series_uri)

            if series_id != -1:
                if series_id not in self.seriesDetail:
                    self.seriesDetail[series_id] = {'title': str(series_title), 'uri': str(series_uri)}

            self.seriesId = series_id

    def _save_textObjects(self):
        """
        A set of descriptive text blurbs for the comic.
        """
        for text_obj in self.data['textObjects']:
            textObjectType = ""
            language = ""
            text = ""

            if 'type' in text_obj:
                textObjectType = str(text_obj['type'])
            if 'language' in text_obj:
                language = str(text_obj['language'])
            if 'text' in text_obj:
                text = str(text_obj['text'])

            if textObjectType not in self.textObjects:
                self.textObjects[textObjectType] = [{'language': language, 'text': text}]
            else:
                self.textObjects[textObjectType].append({'language': language, 'text': text})

    def _save_upc(self):
        """
        The UPC barcode number for the comic (generally only populated for periodical formats).
        """
        if 'upc' in self.data and self.data['upc'] is not None:
            self.upc = str(self.data['upc'])

    def _save_variantDescription(self):
        """
        If the issue is a variant (e.g. an alternate cover, second printing, or director’s cut),
        a text description of the variant.
        """
        if 'variantDescription' in self.data and self.data['variantDescription'] is not None:
            self.variantDescription = str(self.data['variantDescription'])

    def _save_variants(self):
        """
        A list of variant issues for this comic
        (includes the "original" issue if the current issue is a variant).
        """

        for variant in self.data['variants']:
            variant_uri = variant['resourceURI']
            variant_title = variant['name']
            variant_id = self.get_id_from_resourceURI(variant_uri)

            if "Variant" in variant_title:
                isVariant = True

            if variant_id != -1:
                # used for creating new comic book record for variant
                if variant_id not in self.variantDetail and variant_id != self.id:
                    self.variantDetail[variant_id] = {'title': variant_title, 'uri': variant_uri, 'isVariant': True}

    ####################################################################################################################
    #
    #                                   ADD NEW RECORDS TO DATABASE
    #
    ####################################################################################################################

    def _add_new_variant(self):
        """
        Uploads any variant comic records that do not already exist in the comic_books.comics table
        """
        for variant in self.variantDetail:
            variant_id = variant
            variant_title = self.variantDetail[variant_id]['title']
            variant_uri = self.variantDetail[variant_id]['uri']
            isVariant = self.variantDetail[variant_id]['isVariant']

            self.db.upload_new_variants_record(variant_id, variant_title, variant_uri, self.issueNumber, isVariant)

    ####################################################################################################################
    #
    #                               Comics_has_Relationships
    #
    ####################################################################################################################
    def _comics_has_variants(self):
        """
        Upload new record in Comics_has_Events table
        """

        for variant_id in self.variantDetail:
            self.db.upload_new_comics_has_variants_record(int(self.id), int(variant_id))
