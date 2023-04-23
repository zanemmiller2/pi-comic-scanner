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
            self, db_connection, response_data, isPurchasedDate: str = None, isPurchasedPrice: float = None,
            isPurchasedType: str = None, isPurchased: bool = False
            ):
        """ Represents a Comic book based on the marvel comic developer api json response model """
        super().__init__(db_connection, response_data)
        self.count = None  # int, optional
        self.digitalId = None  # int, optional
        self.title = None  # string, optional
        self.issueNumber = None  # double, optional
        self.variantDescription = None  # string, optional
        self.description = None  # string, optional
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
        self.originalIssueId = None
        self.onSaleDate = None
        self.focDate = None
        self.unlimitedDate = None
        self.digitalPurchaseDate = None
        self.printPrice = None
        self.digitalPurchasePrice = None
        self.variantDetail = {}  # (variantDetail[variant_id] = {title: '', uri: ''})
        self.creatorDetail = {}  # (creatorDetail[creator_id] = {f_name: '', m_name: '', l_name: '', uri: ''})
        self.creatorIds = {}  # (creatorIds[creator_id] = [roles]}) ...comics_has...
        self.characterDetail = {}  # (characterDetail[character_id] = {name: '', uri: ''})

        self.isPurchased = isPurchased
        self.isPurchasedDate = self.convert_to_SQL_date(isPurchasedDate)
        self.isPurchasedPrice = isPurchasedPrice
        self.isPurchasedType = isPurchasedType.title()

    '''
    ####################################################################################################################
    #
    #                                   MAIN CONTROL FLOW FUNCTIONS
    #
    ####################################################################################################################
    '''

    def save_properties(self):
        """
        Maps the json response to member class variables
        """
        if self.data:
            # Unique to ComicBook() class
            self._save_characters()
            self._save_creators()
            self._save_dates()
            self._save_description()
            self._save_diamondCode()
            self._save_digitalId()
            self._save_ean()
            self._save_events()
            self._save_format()
            self._save_images()
            self._save_isbn()
            self._save_issn()
            self._save_issueNumber()
            self._save_pageCount()
            self._save_prices()
            self._save_series()
            self._save_stories()
            self._save_textObjects()
            self._save_title()
            self._save_upc()
            self._save_variantDescription()
            self._save_variants()

            # From Parent class
            self._save_id()
            self._save_modified()
            self._save_resourceURI()
            self._save_urls()
            self._save_thumbnail()

    def upload_new_records(self):
        """
        Uploads new records to the database before uploading the entire comic book with relevant foreign keys
        """
        # Unique to ComicBook() class
        self._add_new_variant()
        self._add_new_creator()
        self._add_new_character()

        # From parent class
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
        comic_detailURL = None
        comic_purchaseURL = None
        comic_readerURL = None
        comic_inAppLinkURL = None
        for url_type, url_str in self.urls:
            if url_type == 'detail':
                comic_detailURL = url_str
            elif url_type == 'purchase':
                comic_purchaseURL = url_str
            elif url_type == 'reader':
                comic_readerURL = url_str
            elif url_type == 'inAppLink':
                comic_inAppLinkURL = url_str

        params = (self.id, self.digitalId, self.title, self.issueNumber, self.variantDescription, self.description,
                  self.modified, self.isbn, self.upc, self.diamondCode, self.ean, self.issn, self.format,
                  self.pageCount, json.dumps(self.textObjects), self.resourceURI, comic_detailURL, comic_purchaseURL,
                  comic_readerURL, comic_inAppLinkURL, self.onSaleDate, self.focDate, self.unlimitedDate,
                  self.digitalPurchaseDate, self.printPrice, self.digitalPurchasePrice, self.seriesId, self.thumbnail,
                  self.thumbnailExtension, self.originalIssueId)

        self.db.upload_complete_comic_book(params)

    def upload_comics_has_relationships(self):
        """
        Runs through and creates all the comics_has_relationships
        """
        self._comics_has_characters()
        self._comics_has_creators()
        self._comics_has_events()
        self._comics_has_images()
        self._comics_has_stories()
        self._comics_has_urls()
        self._comics_has_variants()

        if self.isPurchased is True:
            self._upload_purchasedComic()

    def _upload_purchasedComic(self):
        """ Uploads a purchased comic to the PurchasedComics table """

        params = (self.id, self.isPurchasedDate, self.isPurchasedPrice, self.isPurchasedType, self.isPurchasedDate,
                  self.isPurchasedPrice, self.isPurchasedType)
        self.db.upload_complete_purchased_comic(params)

    '''
    ####################################################################################################################
    #
    #          ADD NEW JSON RESPONSE DATA TO CLASS VARIABLES
    #
    ####################################################################################################################
    '''

    def _save_characters(self):
        """
        A resource list containing the characters which appear in this comic.
        """
        if self.data['characters']['available'] > 0:
            for character in self.data['characters']['items']:
                character_resource_uri = character['resourceURI']
                character_name = character['name']
                character_id = self.get_id_from_resourceURI(character_resource_uri)

                if character_id != -1:
                    # Save to dict for creating new character record
                    if character_id not in self.characterDetail:
                        self.characterDetail[character_id] = {
                            'name': character_name,
                            'uri': character_resource_uri
                        }

    def _save_creators(self):
        """
        A resource list containing the creators associated with this comic.
        """
        if self.data['creators']['available'] > 0:
            for creator in self.data['creators']['items']:
                creator_resource_uri = creator['resourceURI']
                creator_name = creator['name']
                creator_role = creator['role']
                creator_id = self.get_id_from_resourceURI(creator_resource_uri)
                creator_first_name, creator_middle_name, creator_last_name = self.get_split_name(creator_name)

                if creator_id != -1:

                    # save it to the detail dictionary for creating new db record
                    if creator_id not in self.creatorDetail:
                        self.creatorDetail[creator_id] = {
                            'first_name': creator_first_name,
                            'middle_name': creator_middle_name,
                            'last_name': creator_last_name,
                            'uri': creator_resource_uri
                        }

                    # save to creatorIds dictionary with role for Comics_has_Creators entity
                    if creator_id not in self.creatorIds:
                        self.creatorIds[creator_id] = [creator_role]
                    else:
                        self.creatorIds[creator_id].append(creator_role)

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

    def _save_description(self):
        """
        The preferred description of the comic.
        """
        self.description = str(self.data['description'])

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

        if self.data['series']:
            series_uri = self.data['series']['resourceURI']
            series_title = self.data['series']['name']
            series_id = self.get_id_from_resourceURI(series_uri)

            if series_id != -1:
                if series_id not in self.seriesDetail:
                    self.seriesDetail[series_id] = {'title': series_title, 'uri': series_uri}

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

    def _save_title(self):
        """
        The canonical title of the comic.
        """
        self.title = str(self.data['title'])

    def _save_upc(self):
        """
        The UPC barcode number for the comic (generally only populated for periodical formats).
        """
        self.upc = str(self.data['upc'])

    def _save_variantDescription(self):
        """
        If the issue is a variant (e.g. an alternate cover, second printing, or director’s cut),
        a text description of the variant.
        """
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

    def _add_new_character(self):
        """
        Adds new character to comic_books.characters table if record does not exist
        """

        for character in self.characterDetail:
            character_id = character
            character_name = self.characterDetail[character_id]['name']
            character_resource_uri = self.characterDetail[character_id]['uri']

            self.db.upload_new_character_record(character_id, character_name, character_resource_uri)

    def _add_new_creator(self):
        """
        Adds new creator records to comic_books.creators with resourceURI, id, and first, middle and last names
        """
        for creator in self.creatorDetail:
            creator_id = creator
            f_name = self.creatorDetail[creator_id]['first_name']
            m_name = self.creatorDetail[creator_id]['middle_name']
            l_name = self.creatorDetail[creator_id]['last_name']
            resource_uri = self.creatorDetail[creator_id]['uri']

            self.db.upload_new_creator_record(creator_id, f_name, m_name, l_name, resource_uri)

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

    def _comics_has_characters(self):
        """
        Upload new record in Comics_has_Characters table
        """
        for characterId in self.characterDetail:
            self.db.upload_new_comics_has_characters_record(int(self.id), int(characterId))

    def _comics_has_creators(self):
        """
        Upload new record in Comics_has_Creators table
        """
        for creator in self.creatorIds:
            creator_id = creator
            for role in self.creatorIds[creator_id]:
                self.db.upload_new_comics_has_creators_record(int(self.id), int(creator_id), str(role))

    def _comics_has_events(self):
        """
        Upload new record in Comics_has_Events table
        """
        for eventId in self.eventDetail:
            self.db.upload_new_comics_has_events_record(int(self.id), int(eventId))

    def _comics_has_images(self):
        """
        Upload new record in Comics_has_Events table
        """
        for image_path, image_extension in self.image_paths:
            self.db.upload_new_comics_has_images_record(int(self.id), str(image_path))

    def _comics_has_stories(self):
        """
        Upload new record in Comics_has_Events table
        """
        for story in self.storyDetail:
            self.db.upload_new_comics_has_stories_record(int(self.id), int(story))

    def _comics_has_urls(self):
        """
        Upload new record in Comics_has_Events table
        """
        for url_type, url_str in self.urls:
            self.db.upload_new_comics_has_urls_record(int(self.id), str(url_str))

    def _comics_has_variants(self):
        """
        Upload new record in Comics_has_Events table
        """

        for variant_id in self.variantDetail:
            self.db.upload_new_comics_has_variants_record(int(self.id), int(variant_id))
