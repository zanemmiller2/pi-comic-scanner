from flask_mysqldb import MySQL

from app import app
from app.models.Character import Character
from app.models.Comic import Comic
from app.models.Creator import Creator
from app.models.Event import Event
from app.models.Image import Image
from app.models.Series import Series
from app.models.Story import Story


class DB:
    """
    Database Control Class
    """

    def __init__(self):
        self.mysql = MySQL(app)

    def get_purchased_comics(self):
        """ Gets list of all purchased comics and their id, title, issue number, thumbnail """
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
        return [Comic(item) for item in cursor]

    ##################################################################################################
    #
    #           COMIC DETAIL PAGE
    #
    ##################################################################################################
    def get_comic_characters(self, comic_id: int) -> list[Character]:
        """ Get the Event records for the related comic """
        cursor = self.mysql.connection.cursor()
        params = (comic_id,)
        characters_query = \
            "SELECT Cha.*, I.pathExtension as thumbnailExtension " \
            "FROM Comics_has_Characters ChCha " \
            "INNER JOIN Characters Cha " \
            "ON ChCha.characterId = Cha.id " \
            "LEFT JOIN Images I " \
            "ON Cha.thumbnail = I.path " \
            "WHERE ChCha.comicId=%s;"

        cursor.execute(characters_query, params)
        character_details = [Character(item) for item in cursor]

        url_query = \
            "SELECT ChCha.characterId, " \
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
            "WHERE ChCha.comicId=%s;"
        cursor.execute(url_query, params)

        for url in cursor:
            for character in character_details:

                if character.id == url['characterId']:
                    character.update_attributes(url)

        return character_details

    def get_comic_creators(self, comic_id: int) -> list[Creator]:
        """ Get the creator records for the related comic """
        cursor = self.mysql.connection.cursor()
        params = (comic_id,)
        creators_query = \
            "SELECT ChCr.creatorRole as role, Cr.*, I.pathExtension as thumbnailExtension " \
            "FROM Comics_has_Creators ChCr " \
            "INNER JOIN Creators Cr " \
            "ON ChCr.creatorId = Cr.id " \
            "LEFT JOIN Images I " \
            "ON Cr.thumbnail = I.path " \
            "WHERE ChCr.comicId=%s;"

        cursor.execute(creators_query, params)
        creator_details = [Creator(item) for item in cursor]

        url_query = \
            "SELECT ChCr.creatorId, " \
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
            "WHERE ChCr.comicId=%s;"

        cursor.execute(url_query, params)

        for url in cursor:
            for creator in creator_details:

                if creator.id == url['creatorId']:
                    creator.update_attributes(url)

        return creator_details

    def get_single_comic_detail(self, comic_id: int) -> Comic:
        """ Get the comic record by id and the related urls """
        cursor = self.mysql.connection.cursor()
        params = (comic_id,)

        detail_query = \
            "SELECT Comics.*, Images.pathExtension AS thumbnailExtension " \
            "FROM Comics " \
            "LEFT JOIN Images " \
            "ON Comics.thumbnail = Images.path " \
            "WHERE Comics.id=%s;"

        cursor.execute(detail_query, params)
        comic_details = [Comic(item) for item in cursor]

        url_query = \
            "SELECT " \
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
            "WHERE C.id=%s;"
        cursor.execute(url_query, params)

        for url in cursor:
            comic_details[0].update_attributes(url)

        return comic_details[0]

    def get_comic_events(self, comic_id: int) -> list[Event]:
        """ Get the Event records for the related comic """
        cursor = self.mysql.connection.cursor()
        params = (comic_id,)
        events_query = \
            "SELECT E.*, I.pathExtension as thumbnailExtension " \
            "FROM Comics_has_Events ChE " \
            "INNER JOIN Events E " \
            "ON ChE.eventId = E.id " \
            "LEFT JOIN Images I " \
            "ON E.thumbnail = I.path " \
            "WHERE ChE.comicId=%s;"

        cursor.execute(events_query, params)
        event_details = [Event(item) for item in cursor]

        url_query = \
            "SELECT ChE.eventId, " \
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
            "WHERE ChE.comicId=%s;"

        cursor.execute(url_query, params)

        for url in cursor:
            for event in event_details:

                if event.id == url['eventId']:
                    event.update_attributes(url)

        return event_details

    def get_comic_images(self, comic_id: int) -> list[Image]:
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
        return [Image(item) for item in cursor]

    def get_single_series_detail(self, series_id: int) -> Series:
        """ Gets the comics related Series's details """
        cursor = self.mysql.connection.cursor()
        params = (series_id,)

        detail_query = \
            "SELECT Series.*, Images.pathExtension AS thumbnailExtension " \
            "FROM Series " \
            "LEFT JOIN Images " \
            "ON Series.thumbnail = Images.path " \
            "WHERE Series.id=%s;"
        cursor.execute(detail_query, params)

        series_details = [Series(item) for item in cursor]

        url_query = \
            "SELECT " \
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
            "WHERE S.id=%s;"
        cursor.execute(url_query, params)

        for url in cursor:
            series_details[0].update_attributes(url)

        return series_details[0]

    def get_comic_stories(self, comic_id: int) -> list[Story]:
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
        story_details = [Story(item) for item in cursor]

        interior_story_query = \
            "SELECT Stories.*, I.pathExtension AS thumbnailExtension from Comics_has_Stories ChS " \
            "INNER JOIN Stories " \
            "ON ChS.storyId = Stories.id AND (Stories.type = 'interiorStory' OR Stories.type = 'story') " \
            "LEFT JOIN Images I " \
            "on Stories.thumbnail = I.path " \
            "WHERE ChS.comicId=%s;"

        cursor.execute(interior_story_query, params)
        for interiorStory in cursor:
            story_details[0].update_attributes(interiorStory, 'interiorStory')

        return story_details

    def get_comic_variants(self, comic_id: int) -> list[Comic]:
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
        variant_details = [Comic(item) for item in cursor]

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

        return variant_details
