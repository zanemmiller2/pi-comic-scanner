from app import mysqldb
from app.frontendModels.Character import FrontEndCharacter
from app.frontendModels.Comic import FrontEndComic
from app.frontendModels.Creator import FrontEndCreator
from app.frontendModels.Event import FrontEndEvent
from app.frontendModels.Image import FrontEndImage
from app.frontendModels.Series import FrontEndSeries
from app.frontendModels.Story import FrontEndStory


class FrontEndDB:
    """
    Database Control Class
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
    PURCHASED_COMICS_ENTITY = 'PurchasedComics'
    ENTITIES = (CHARACTER_ENTITY, COMIC_ENTITY, CREATOR_ENTITY, EVENT_ENTITY, IMAGE_ENTITY,
                SERIES_ENTITY, STORY_ENTITY, URL_ENTITY, PURCHASED_COMICS_ENTITY)

    def __init__(self):
        self.mysql = mysqldb

        if self.mysql:
            print("FrontEndDB CONNECTED...")

    def get_purchased_comics(self) -> list[FrontEndComic]:
        """
        Gets list of all purchased comics and their id, title, issue number, thumbnail
        """
        cursor = self.mysql.connection.cursor()
        query = \
            "SELECT PC.*, C.*, I.pathExtension as thumbnailExtension " \
            "FROM PurchasedComics PC " \
            "INNER JOIN Comics C " \
            "ON C.id = PC.comicId " \
            "INNER JOIN Images I " \
            "ON C.thumbnail = I.path;"

        params = ()
        cursor.execute(query, params)
        return [FrontEndComic(comic) for comic in cursor]

    def get_purchased_comics_related_series(self) -> list[FrontEndSeries]:
        """
        Gets list of all series related to purchased comics and their id, title, thumbnail
        """
        cursor = self.mysql.connection.cursor()
        query = \
            "SELECT DISTINCT S.*, I.pathExtension as thumbnailExtension " \
            "FROM PurchasedComics PC " \
            "INNER JOIN Comics C " \
            "on PC.comicId = C.id " \
            "LEFT JOIN Series S " \
            "on C.seriesId = S.id " \
            "LEFT JOIN Images I " \
            "on S.thumbnail = I.path;"
        params = ()
        cursor.execute(query, params)
        return [FrontEndSeries(series) for series in cursor]

    ##################################################################################################
    #
    #           COMIC DETAIL PAGE
    #
    ##################################################################################################
    def get_comic_characters(self, comic_id: int) -> list[FrontEndCharacter]:
        """ Get the Event records for the related comic """
        cursor = self.mysql.connection.cursor()
        params = (comic_id,)
        characters_query = \
            "SELECT Cha.*, I.pathExtension as thumbnailExtension, " \
            "(SELECT ChhUrl.url " \
            "FROM Characters_has_URLs ChhUrl " \
            "LEFT JOIN URLs UL " \
            "ON ChhUrl.url = UL.url " \
            "WHERE ChhUrl.characterId = ChCha.characterId AND UL.type = 'purchase') as purchaseURL, " \
            "(SELECT ChhUrl.url " \
            "FROM Characters_has_URLs ChhUrl " \
            "LEFT JOIN URLs UL " \
            "ON ChhUrl.url = UL.url " \
            "WHERE ChhUrl.characterId = ChCha.characterId AND UL.type = 'detail') as detailURL, " \
            "(SELECT ChhUrl.url " \
            "FROM Characters_has_URLs ChhUrl " \
            "LEFT JOIN URLs UL " \
            "ON ChhUrl.url = UL.url " \
            "WHERE ChhUrl.characterId = ChCha.characterId AND UL.type = 'comiclink') as comicLink, " \
            "(SELECT ChhUrl.url " \
            "FROM Characters_has_URLs ChhUrl " \
            "LEFT JOIN URLs UL " \
            "ON ChhUrl.url = UL.url " \
            "WHERE ChhUrl.characterId = ChCha.characterId AND UL.type = 'reader') as readerURL, " \
            "(SELECT ChhUrl.url " \
            "FROM Characters_has_URLs ChhUrl " \
            "LEFT JOIN URLs UL " \
            "ON ChhUrl.url = UL.url " \
            "WHERE ChhUrl.characterId = ChCha.characterId AND UL.type = 'inAppLink') as inAppLink, " \
            "(SELECT ChhUrl.url " \
            "FROM Characters_has_URLs ChhUrl " \
            "LEFT JOIN URLs UL " \
            "ON ChhUrl.url = UL.url " \
            "WHERE ChhUrl.characterId = ChCha.characterId AND UL.type = 'wiki') as wiki " \
            "FROM Comics_has_Characters ChCha " \
            "LEFT JOIN Characters Cha " \
            "on ChCha.characterId = Cha.id " \
            "LEFT JOIN Images I " \
            "on Cha.thumbnail = I.path " \
            "WHERE ChCha.comicId=%s;"

        cursor.execute(characters_query, params)
        return [FrontEndCharacter(item) for item in cursor]

    def get_comic_creators(self, comic_id: int) -> list[FrontEndCreator]:
        """ Get the creator records for the related comic """
        cursor = self.mysql.connection.cursor()
        params = (comic_id,)
        creators_query = \
            "SELECT Cr.*, I.pathExtension as thumbnailExtension, " \
            "(SELECT CrhUrl.url " \
            "FROM Creators_has_URLs CrhUrl " \
            "LEFT JOIN URLs UL " \
            "ON CrhUrl.url = UL.url " \
            "WHERE CrhUrl.creatorId = ChCr.creatorId AND UL.type = 'purchase') as purchaseURL, " \
            "(SELECT CrhUrl.url " \
            "FROM Creators_has_URLs CrhUrl " \
            "LEFT JOIN URLs UL " \
            "ON CrhUrl.url = UL.url " \
            "WHERE CrhUrl.creatorId = ChCr.creatorId AND UL.type = 'detail') as detailURL, " \
            "(SELECT CrhUrl.url " \
            "FROM Creators_has_URLs CrhUrl " \
            "LEFT JOIN URLs UL " \
            "ON CrhUrl.url = UL.url " \
            "WHERE CrhUrl.creatorId = ChCr.creatorId AND UL.type = 'comiclink') as comicLink, " \
            "(SELECT CrhUrl.url " \
            "FROM Creators_has_URLs CrhUrl " \
            "LEFT JOIN URLs UL " \
            "ON CrhUrl.url = UL.url " \
            "WHERE CrhUrl.creatorId = ChCr.creatorId AND UL.type = 'reader') as readerURL, " \
            "(SELECT CrhUrl.url " \
            "FROM Creators_has_URLs CrhUrl " \
            "LEFT JOIN URLs UL " \
            "ON CrhUrl.url = UL.url " \
            "WHERE CrhUrl.creatorId = ChCr.creatorId AND UL.type = 'inAppLink') as inAppLink, " \
            "(SELECT CrhUrl.url " \
            "FROM Creators_has_URLs CrhUrl " \
            "LEFT JOIN URLs UL " \
            "ON CrhUrl.url = UL.url " \
            "WHERE CrhUrl.creatorId = ChCr.creatorId AND UL.type = 'wiki') as wiki " \
            "FROM Comics_has_Creators ChCr " \
            "LEFT JOIN Creators Cr " \
            "on ChCr.creatorId = Cr.id " \
            "LEFT JOIN Images I " \
            "on Cr.thumbnail = I.path " \
            "WHERE ChCr.comicId=%s;"

        cursor.execute(creators_query, params)
        return [FrontEndCreator(creator) for creator in cursor]

    def get_single_comic_detail(self, comic_id: int) -> list[FrontEndComic]:
        """ Get the comic record by id and the related urls """
        cursor = self.mysql.connection.cursor()
        params = (comic_id,)

        detail_query = \
            "SELECT C.*, PurchasedComics.*, Images.pathExtension AS thumbnailExtension, " \
            "(SELECT ChUL.url " \
            "FROM Comics_has_URLs ChUL " \
            "LEFT OUTER JOIN URLs UL " \
            "ON ChUL.url = UL.url " \
            "WHERE ChUL.comicId = C.id AND UL.type = 'purchase') as purchaseURL, " \
            "(SELECT ChUL.url " \
            "FROM Comics_has_URLs ChUL " \
            "LEFT OUTER JOIN URLs UL " \
            "ON ChUL.url = UL.url " \
            "WHERE ChUL.comicId = C.id AND UL.type = 'detail') as detailURL, " \
            "(SELECT ChUL.url " \
            "FROM Comics_has_URLs ChUL " \
            "LEFT OUTER JOIN URLs UL " \
            "ON ChUL.url = UL.url " \
            "WHERE ChUL.comicId = C.id AND UL.type = 'comiclink') as comicLink, " \
            "(SELECT ChUL.url " \
            "FROM Comics_has_URLs ChUL " \
            "LEFT OUTER JOIN URLs UL " \
            "ON ChUL.url = UL.url " \
            "WHERE ChUL.comicId = C.id AND UL.type = 'reader') as readerURL, " \
            "(SELECT ChUL.url " \
            "FROM Comics_has_URLs ChUL " \
            "LEFT OUTER JOIN URLs UL " \
            "ON ChUL.url = UL.url " \
            "WHERE ChUL.comicId = C.id AND UL.type = 'inAppLink') as inAppLink, " \
            "(SELECT ChUL.url " \
            "FROM Comics_has_URLs ChUL " \
            "LEFT OUTER JOIN URLs UL " \
            "ON ChUL.url = UL.url " \
            "WHERE ChUL.comicId = C.id AND UL.type = 'wiki') as wiki " \
            "FROM Comics C " \
            "LEFT JOIN Images " \
            "ON C.thumbnail = Images.path " \
            "LEFT JOIN PurchasedComics " \
            "ON C.id = PurchasedComics.comicId " \
            "WHERE C.id=%s;"

        cursor.execute(detail_query, params)
        return [FrontEndComic(comic) for comic in cursor]

    def get_comic_events(self, comic_id: int) -> list[FrontEndEvent]:
        """ Get the Event records for the related comic """
        cursor = self.mysql.connection.cursor()
        params = (comic_id,)
        events_query = \
            "SELECT E.*, I.pathExtension as thumbnailExtension, " \
            "(SELECT EhUrl.url " \
            "FROM Events_has_URLs EhUrl " \
            "LEFT JOIN URLs UL " \
            "ON EhUrl.url = UL.url " \
            "WHERE EhUrl.eventId = ChE.eventId AND UL.type = 'purchase') as purchaseURL, " \
            "(SELECT EhUrl.url " \
            "FROM Events_has_URLs EhUrl " \
            "LEFT JOIN URLs UL " \
            "ON EhUrl.url = UL.url " \
            "WHERE EhUrl.eventId = ChE.eventId AND UL.type = 'detail') as detailURL, " \
            "(SELECT EhUrl.url " \
            "FROM Events_has_URLs EhUrl " \
            "LEFT JOIN URLs UL " \
            "ON EhUrl.url = UL.url " \
            "WHERE EhUrl.eventId = ChE.eventId AND UL.type = 'comiclink') as comicLink, " \
            "(SELECT EhUrl.url " \
            "FROM Events_has_URLs EhUrl " \
            "LEFT JOIN URLs UL " \
            "ON EhUrl.url = UL.url " \
            "WHERE EhUrl.eventId = ChE.eventId AND UL.type = 'reader') as readerURL, " \
            "(SELECT EhUrl.url " \
            "FROM Events_has_URLs EhUrl " \
            "LEFT JOIN URLs UL " \
            "ON EhUrl.url = UL.url " \
            "WHERE EhUrl.eventId = ChE.eventId AND UL.type = 'inAppLink') as inAppLink, " \
            "(SELECT EhUrl.url " \
            "FROM Events_has_URLs EhUrl " \
            "LEFT JOIN URLs UL " \
            "ON EhUrl.url = UL.url " \
            "WHERE EhUrl.eventId = ChE.eventId AND UL.type = 'wiki') as wiki " \
            "FROM Comics_has_Events ChE " \
            "LEFT JOIN Events E " \
            "on ChE.eventId = E.id " \
            "LEFT JOIN Images I " \
            "on E.thumbnail = I.path " \
            "WHERE ChE.comicId=%s;"

        cursor.execute(events_query, params)
        return [FrontEndEvent(event) for event in cursor]

    def get_comic_images(self, comic_id: int) -> list[FrontEndImage]:
        """ Get the current comics variant comics """
        cursor = self.mysql.connection.cursor()
        params = (comic_id,)
        images_query = \
            "SELECT ChI.imagePath as thumbnail, I.pathExtension as thumbnailExtension " \
            "FROM Comics_has_Images ChI " \
            "LEFT JOIN Images I " \
            "on ChI.imagePath = I.path " \
            "WHERE ChI.comicId = %s;"

        cursor.execute(images_query, params)
        return [FrontEndImage(item) for item in cursor]

    def get_comic_stories(self, comic_id: int) -> list[FrontEndStory]:
        """ Get the stories for a specific comic """
        cursor = self.mysql.connection.cursor()
        params = (comic_id,)

        cover_story_query = \
            "SELECT Stories.*, I.pathExtension AS thumbnailExtension from Comics_has_Stories ChS " \
            "INNER JOIN Stories " \
            "ON ChS.storyId = Stories.id AND Stories.type = 'cover' " \
            "LEFT JOIN Images I " \
            "on Stories.thumbnail = I.path " \
            "WHERE ChS.comicId=%s;"

        cursor.execute(cover_story_query, params)
        story_details = [FrontEndStory(item) for item in cursor]

        interior_story_query = \
            "SELECT Stories.*, I.pathExtension AS thumbnailExtension from Comics_has_Stories ChS " \
            "INNER JOIN Stories " \
            "ON ChS.storyId = Stories.id AND (Stories.type = 'interiorStory' OR Stories.type = 'story') " \
            "LEFT JOIN Images I " \
            "on Stories.thumbnail = I.path " \
            "WHERE ChS.comicId=%s;"

        cursor.execute(interior_story_query, params)
        for interiorStory in cursor:
            story_details[0].update_attributes(attributes=interiorStory, qualifier='interiorStory')

        return story_details

    def get_comic_variants(self, comic_id: int) -> list[FrontEndComic]:
        """ Get the current comics variant comics """
        cursor = self.mysql.connection.cursor()
        params = (comic_id,)
        variants_query = \
            "SELECT C.*, I.pathExtension as thumbnailExtension " \
            "FROM Comics_has_Variants ChV " \
            "INNER JOIN Comics C " \
            "on ChV.variantId = C.id " \
            "LEFT JOIN Images I " \
            "on C.thumbnail = I.path " \
            "WHERE ChV.comicId = %s;"

        cursor.execute(variants_query, params)
        variant_details = [FrontEndComic(item) for item in cursor]

        url_query = \
            "SELECT ChV.variantId, " \
            "(SELECT ChUL.url " \
            "FROM Comics_has_URLs ChUL " \
            "LEFT OUTER JOIN URLs UL " \
            "ON ChUL.url = UL.url " \
            "WHERE ChUL.comicId = ChV.variantId AND UL.type = 'purchase') as purchaseURL, " \
            "(SELECT ChUL.url " \
            "FROM Comics_has_URLs ChUL " \
            "LEFT OUTER JOIN URLs UL " \
            "ON ChUL.url = UL.url " \
            "WHERE ChUL.comicId = ChV.variantId AND UL.type = 'detail') as detailURL, " \
            "(SELECT ChUL.url " \
            "FROM Comics_has_URLs ChUL " \
            "LEFT OUTER JOIN URLs UL " \
            "ON ChUL.url = UL.url " \
            "WHERE ChUL.comicId = ChV.variantId AND UL.type = 'comiclink') as comicLink, " \
            "(SELECT ChUL.url " \
            "FROM Comics_has_URLs ChUL " \
            "LEFT OUTER JOIN URLs UL " \
            "ON ChUL.url = UL.url " \
            "WHERE ChUL.comicId = ChV.variantId AND UL.type = 'reader') as readerURL, " \
            "(SELECT ChUL.url " \
            "FROM Comics_has_URLs ChUL " \
            "LEFT OUTER JOIN URLs UL " \
            "ON ChUL.url = UL.url " \
            "WHERE ChUL.comicId = ChV.variantId AND UL.type = 'inAppLink') as inAppLink, " \
            "(SELECT ChUL.url " \
            "FROM Comics_has_URLs ChUL " \
            "LEFT OUTER JOIN URLs UL " \
            "ON ChUL.url = UL.url " \
            "WHERE ChUL.comicId = ChV.variantId AND UL.type = 'wiki') as wiki " \
            "FROM Comics_has_Variants ChV " \
            "WHERE ChV.comicId=%s;"

        cursor.execute(url_query, params)

        for url in cursor:
            for variant in variant_details:

                if variant.id == url['variantId']:
                    variant.update_attributes(url)
                    break

        return variant_details

    ##################################################################################################
    #
    #           SERIES DETAIL PAGE
    #
    ##################################################################################################

    def get_single_series_detail(self, series_id: int) -> list[FrontEndSeries]:
        """ Gets the comics related Series's details """
        cursor = self.mysql.connection.cursor()
        params = (series_id,)

        detail_query = \
            "SELECT S.*, " \
            "Images.pathExtension AS thumbnailExtension, " \
            "(SELECT ShUL.url " \
            "FROM Series_has_URLs ShUL " \
            "LEFT JOIN URLs UL " \
            "ON ShUL.url = UL.url " \
            "WHERE ShUL.seriesId = S.id AND UL.type = 'purchase') as purchaseURL, " \
            "(SELECT ShUL.url " \
            "FROM Series_has_URLs ShUL " \
            "LEFT JOIN URLs UL " \
            "ON ShUL.url = UL.url " \
            "WHERE ShUL.seriesId = S.id AND UL.type = 'detail') as detailURL, " \
            "(SELECT ShUL.url " \
            "FROM Series_has_URLs ShUL " \
            "LEFT JOIN URLs UL " \
            "ON ShUL.url = UL.url " \
            "WHERE ShUL.seriesId = S.id AND UL.type = 'comiclink') as comicLink, " \
            "(SELECT ShUL.url " \
            "FROM Series_has_URLs ShUL " \
            "LEFT JOIN URLs UL " \
            "ON ShUL.url = UL.url " \
            "WHERE ShUL.seriesId = S.id AND UL.type = 'reader') as readerURL, " \
            "(SELECT ShUL.url " \
            "FROM Series_has_URLs ShUL " \
            "LEFT JOIN URLs UL " \
            "ON ShUL.url = UL.url " \
            "WHERE ShUL.seriesId = S.id AND UL.type = 'inAppLink') as inAppLink, " \
            "(SELECT ShUL.url " \
            "FROM Series_has_URLs ShUL " \
            "LEFT JOIN URLs UL " \
            "ON ShUL.url = UL.url " \
            "WHERE ShUL.seriesId = S.id AND UL.type = 'wiki') as wiki " \
            "FROM Series S " \
            "LEFT JOIN Images " \
            "ON S.thumbnail = Images.path " \
            "WHERE S.id=%s;"

        cursor.execute(detail_query, params)
        return [FrontEndSeries(series) for series in cursor]

    def get_series_characters(self, series_id: int) -> list[FrontEndCharacter]:
        """
        Get the Character records for the related series
        :param series_id: the id of the individual series
        """
        cursor = self.mysql.connection.cursor()
        params = (series_id,)
        characters_query = \
            "SELECT Cha.*, I.pathExtension as thumbnailExtension, " \
            "(SELECT ChhUrl.url " \
            "FROM Characters_has_URLs ChhUrl " \
            "LEFT JOIN URLs UL " \
            "ON ChhUrl.url = UL.url " \
            "WHERE ChhUrl.characterId = ShCha.characterId AND UL.type = 'purchase') as purchaseURL, " \
            "(SELECT ChhUrl.url " \
            "FROM Characters_has_URLs ChhUrl " \
            "LEFT JOIN URLs UL " \
            "ON ChhUrl.url = UL.url " \
            "WHERE ChhUrl.characterId = ShCha.characterId AND UL.type = 'detail') as detailURL, " \
            "(SELECT ChhUrl.url " \
            "FROM Characters_has_URLs ChhUrl " \
            "LEFT JOIN URLs UL " \
            "ON ChhUrl.url = UL.url " \
            "WHERE ChhUrl.characterId = ShCha.characterId AND UL.type = 'comiclink') as comicLink, " \
            "(SELECT ChhUrl.url " \
            "FROM Characters_has_URLs ChhUrl " \
            "LEFT JOIN URLs UL " \
            "ON ChhUrl.url = UL.url " \
            "WHERE ChhUrl.characterId = ShCha.characterId AND UL.type = 'reader') as readerURL, " \
            "(SELECT ChhUrl.url " \
            "FROM Characters_has_URLs ChhUrl " \
            "LEFT JOIN URLs UL " \
            "ON ChhUrl.url = UL.url " \
            "WHERE ChhUrl.characterId = ShCha.characterId AND UL.type = 'inAppLink') as inAppLink, " \
            "(SELECT ChhUrl.url " \
            "FROM Characters_has_URLs ChhUrl " \
            "LEFT JOIN URLs UL " \
            "ON ChhUrl.url = UL.url " \
            "WHERE ChhUrl.characterId = ShCha.characterId AND UL.type = 'wiki') as wiki " \
            "FROM Series_has_Characters ShCha " \
            "LEFT JOIN Characters Cha " \
            "on ShCha.characterId = Cha.id " \
            "LEFT JOIN Images I " \
            "on Cha.thumbnail = I.path " \
            "WHERE ShCha.seriesId=%s;"

        cursor.execute(characters_query, params)
        return [FrontEndCharacter(character) for character in cursor]

    def get_series_events(self, series_id: int) -> list[FrontEndEvent]:
        """
        Get the Event records for the related series
        :param series_id: the id of the individual series
        """
        cursor = self.mysql.connection.cursor()
        params = (series_id,)
        events_query = \
            "SELECT E.*, I.pathExtension as thumbnailExtension, " \
            "(SELECT EhUrl.url " \
            "FROM Events_has_URLs EhUrl " \
            "LEFT JOIN URLs UL " \
            "ON EhUrl.url = UL.url " \
            "WHERE EhUrl.eventId = ShE.eventId AND UL.type = 'purchase') as purchaseURL, " \
            "(SELECT EhUrl.url " \
            "FROM Events_has_URLs EhUrl " \
            "LEFT JOIN URLs UL " \
            "ON EhUrl.url = UL.url " \
            "WHERE EhUrl.eventId = ShE.eventId AND UL.type = 'detail') as detailURL, " \
            "(SELECT EhUrl.url " \
            "FROM Events_has_URLs EhUrl " \
            "LEFT JOIN URLs UL " \
            "ON EhUrl.url = UL.url " \
            "WHERE EhUrl.eventId = ShE.eventId AND UL.type = 'comiclink') as comicLink, " \
            "(SELECT EhUrl.url " \
            "FROM Events_has_URLs EhUrl " \
            "LEFT JOIN URLs UL " \
            "ON EhUrl.url = UL.url " \
            "WHERE EhUrl.eventId = ShE.eventId AND UL.type = 'reader') as readerURL, " \
            "(SELECT EhUrl.url " \
            "FROM Events_has_URLs EhUrl " \
            "LEFT JOIN URLs UL " \
            "ON EhUrl.url = UL.url " \
            "WHERE EhUrl.eventId = ShE.eventId AND UL.type = 'inAppLink') as inAppLink, " \
            "(SELECT EhUrl.url " \
            "FROM Events_has_URLs EhUrl " \
            "LEFT JOIN URLs UL " \
            "ON EhUrl.url = UL.url " \
            "WHERE EhUrl.eventId = ShE.eventId AND UL.type = 'wiki') as wiki " \
            "FROM Series_has_Events ShE " \
            "LEFT JOIN Events E " \
            "on ShE.eventId = E.id " \
            "LEFT JOIN Images I " \
            "on E.thumbnail = I.path " \
            "WHERE ShE.seriesId=%s;"

        cursor.execute(events_query, params)
        return [FrontEndEvent(event) for event in cursor]

    def get_series_creators(self, series_id: int) -> list[FrontEndCreator]:
        """ Get the creator records for the related comic """
        cursor = self.mysql.connection.cursor()
        params = (series_id,)
        creators_query = \
            "SELECT Cr.*, I.pathExtension as thumbnailExtension, " \
            "(SELECT CrhUrl.url " \
            "FROM Creators_has_URLs CrhUrl " \
            "LEFT JOIN URLs UL " \
            "ON CrhUrl.url = UL.url " \
            "WHERE CrhUrl.creatorId = ShCr.creatorId AND UL.type = 'purchase') as purchaseURL, " \
            "(SELECT CrhUrl.url " \
            "FROM Creators_has_URLs CrhUrl " \
            "LEFT JOIN URLs UL " \
            "ON CrhUrl.url = UL.url " \
            "WHERE CrhUrl.creatorId = ShCr.creatorId AND UL.type = 'detail') as detailURL, " \
            "(SELECT CrhUrl.url " \
            "FROM Creators_has_URLs CrhUrl " \
            "LEFT JOIN URLs UL " \
            "ON CrhUrl.url = UL.url " \
            "WHERE CrhUrl.creatorId = ShCr.creatorId AND UL.type = 'comiclink') as comicLink, " \
            "(SELECT CrhUrl.url " \
            "FROM Creators_has_URLs CrhUrl " \
            "LEFT JOIN URLs UL " \
            "ON CrhUrl.url = UL.url " \
            "WHERE CrhUrl.creatorId = ShCr.creatorId AND UL.type = 'reader') as readerURL, " \
            "(SELECT CrhUrl.url " \
            "FROM Creators_has_URLs CrhUrl " \
            "LEFT JOIN URLs UL " \
            "ON CrhUrl.url = UL.url " \
            "WHERE CrhUrl.creatorId = ShCr.creatorId AND UL.type = 'inAppLink') as inAppLink, " \
            "(SELECT CrhUrl.url " \
            "FROM Creators_has_URLs CrhUrl " \
            "LEFT JOIN URLs UL " \
            "ON CrhUrl.url = UL.url " \
            "WHERE CrhUrl.creatorId = ShCr.creatorId AND UL.type = 'wiki') as wiki " \
            "FROM Series_has_Creators ShCr " \
            "LEFT JOIN Creators Cr " \
            "on ShCr.creatorId = Cr.id " \
            "LEFT JOIN Images I " \
            "on Cr.thumbnail = I.path " \
            "WHERE ShCr.seriesId=%s;"

        cursor.execute(creators_query, params)
        return [FrontEndCreator(creator) for creator in cursor]

    def get_series_stories(self, series_id: int) -> list[FrontEndStory]:
        """ Get the creator records for the related comic """
        cursor = self.mysql.connection.cursor()
        params = (series_id,)
        stories_query = \
            "SELECT St.*, ChSt.comicId, I.pathExtension as thumbnailExtension " \
            "FROM Series_has_Stories ShSt " \
            "LEFT JOIN Stories St " \
            "on ShSt.storyId = St.id " \
            "LEFT JOIN Comics_has_Stories ChSt on ChSt.storyId = St.id " \
            "LEFT JOIN Images I " \
            "on St.thumbnail = I.path " \
            "WHERE ShSt.seriesId=%s;"

        cursor.execute(stories_query, params)
        return [FrontEndStory(story) for story in cursor]
