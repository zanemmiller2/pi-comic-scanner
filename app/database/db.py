from flask_mysqldb import MySQL

from app import app
from app.models.Character import Character
from app.models.Comic import Comic
from app.models.Creator import Creator
from app.models.Event import Event
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
            "LEFT OUTER JOIN URLs UL " \
            "ON ShUL.url = UL.url " \
            "WHERE ShUL.seriesId = S.id AND UL.type = 'purchase') as purchaseURL, " \
            "(SELECT ShUL.url " \
            "FROM Series_has_URLs ShUL " \
            "LEFT OUTER JOIN URLs UL " \
            "ON ShUL.url = UL.url " \
            "WHERE ShUL.seriesId = S.id AND UL.type = 'detail') as detailURL, " \
            "(SELECT ShUL.url " \
            "FROM Series_has_URLs ShUL " \
            "LEFT OUTER JOIN URLs UL " \
            "ON ShUL.url = UL.url " \
            "WHERE ShUL.seriesId = S.id AND UL.type = 'comiclink') as comicLink, " \
            "(SELECT ShUL.url " \
            "FROM Series_has_URLs ShUL " \
            "LEFT OUTER JOIN URLs UL " \
            "ON ShUL.url = UL.url " \
            "WHERE ShUL.seriesId = S.id AND UL.type = 'reader') as readerURL, " \
            "(SELECT ShUL.url " \
            "FROM Series_has_URLs ShUL " \
            "LEFT OUTER JOIN URLs UL " \
            "ON ShUL.url = UL.url " \
            "WHERE ShUL.seriesId = S.id AND UL.type = 'inAppLink') as inAppLink, " \
            "(SELECT ShUL.url " \
            "FROM Series_has_URLs ShUL " \
            "LEFT OUTER JOIN URLs UL " \
            "ON ShUL.url = UL.url " \
            "WHERE ShUL.seriesId = S.id AND UL.type = 'wiki') as wiki " \
            "FROM Series S " \
            "WHERE S.id=%s;"
        cursor.execute(url_query, params)

        for url in cursor:
            series_details[0].update_attributes(url)

        return series_details[0]

    def get_comic_stories(self, comic_id: int) -> Story:
        """ Get the stories for a specific comic """
        cursor = self.mysql.connection.cursor()
        params = (comic_id,)

        cover_story_query = \
            "SELECT Stories.*, I.pathExtension AS thumbnailExtension from Comics_has_Stories ChS " \
            "INNER JOIN Stories " \
            "ON ChS.storyId = Stories.id AND Stories.type = 'cover' " \
            "LEFT OUTER JOIN Images I " \
            "on Stories.thumbnail = I.path " \
            "WHERE ChS.comicId=%s;"

        cursor.execute(cover_story_query, params)
        story_details = [Story(item) for item in cursor]

        interior_story_query = \
            "SELECT Stories.*, I.pathExtension AS thumbnailExtension from Comics_has_Stories ChS " \
            "INNER JOIN Stories " \
            "ON ChS.storyId = Stories.id AND Stories.type = 'interiorStory' " \
            "LEFT OUTER JOIN Images I " \
            "on Stories.thumbnail = I.path " \
            "WHERE ChS.comicId=%s;"

        cursor.execute(interior_story_query, params)
        for interiorStory in cursor:
            story_details[0].update_attributes(interiorStory, 'interiorStory')

        return story_details[0]

    def get_comic_creators(self, comic_id: int) -> list[Creator]:
        """ Get the creator records for the related comic """
        cursor = self.mysql.connection.cursor()
        params = (comic_id,)
        creators_query = \
            "SELECT ChCr.creatorRole, Cr.*, I.pathExtension as thumbnailExtension " \
            "FROM Comics_has_Creators ChCr " \
            "INNER JOIN Creators Cr " \
            "ON ChCr.creatorId = Cr.id " \
            "INNER JOIN Images I " \
            "ON Cr.thumbnail = I.path " \
            "WHERE ChCr.comicId=%s;"

        cursor.execute(creators_query, params)
        return [Creator(item) for item in cursor]

    def get_comic_events(self, comic_id: int) -> list[Event]:
        """ Get the Event records for the related comic """
        cursor = self.mysql.connection.cursor()
        params = (comic_id,)
        events_query = \
            "SELECT E.*, I.pathExtension as thumbnailExtension " \
            "FROM Comics_has_Events ChE " \
            "INNER JOIN Events E " \
            "ON ChE.eventId = E.id " \
            "INNER JOIN Images I " \
            "ON E.thumbnail = I.path " \
            "WHERE ChE.comicId=%s;"

        cursor.execute(events_query, params)
        return [Event(item) for item in cursor]

    def get_comic_characters(self, comic_id: int) -> list[Character]:
        """ Get the Event records for the related comic """
        cursor = self.mysql.connection.cursor()
        params = (comic_id,)
        characters_query = \
            "SELECT Cha.*, I.pathExtension as thumbnailExtension " \
            "FROM Comics_has_Characters ChCha " \
            "INNER JOIN Characters Cha " \
            "ON ChCha.characterId = Cha.id " \
            "INNER JOIN Images I " \
            "ON Cha.thumbnail = I.path " \
            "WHERE ChCha.comicId=%s;"

        cursor.execute(characters_query, params)
        return [Character(item) for item in cursor]
