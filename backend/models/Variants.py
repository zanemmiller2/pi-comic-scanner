from backend.models.ComicBook import ComicBook


class Variant(ComicBook):
    """
    ComicBook object is a map of the marvel public api /comics endpoint response model. The ComicBook object is
    responsible for parsing the response data, creating new database records for specific entities and creating a new
    Comic in the database.
    """

    def __init__(self, db_connection, response_data):
        """ Represents a Comic book based on the marvel comic developer api json response model """

        super().__init__(db_connection, response_data)

        self.ENTITY_NAME = self.COMIC_ENTITY
        _save_variants = None
        _add_new_variant = None
        _comics_has_variants = None
