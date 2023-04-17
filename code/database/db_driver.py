import MySQLdb

from keys import db_credentials


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

    def _connect_to_database(self):
        """
        manages connecting to the database
        :return: the MySQLdb.connect() object
        """
        db_connection = MySQLdb.connect(self._host, self._user, self._passwd, self._db)
        return db_connection

    def upload_upc_to_buffer(self, query_params=(str, str)):
        """
        Uploads a tuple of strings (upc and YYYY-MM-DD) to the scanned_upc_codes table in the comic_books database
        :param query_params: (upc: str, YYYY-MM-DD: str)
        :return: cursor object from connection
        """

        if self._connection is None:
            print(
                "No connection to the database found! Have you called connect_to_database() first?"
            )
            return None

        query = "INSERT INTO comic_books.scanned_upc_codes(upc_code, date_uploaded) VALUES (%s, %s);"

        print("Executing %s with %s" % (query, query_params))
        # Create a cursor to execute query. Why? Because apparently they optimize execution by retaining a reference according to PEP0249

        self.cursor.execute(query, query_params)

        return self.cursor

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

        print("Executing %s" % query)
        # Create a cursor to execute query.
        # Why? Because apparently they optimize execution by retaining a reference according to PEP0249
        self.cursor.execute(query)

        return self.cursor.fetchall()

    def close_db(self):
        """
        Closes the db connection
        """
        self.cursor.close()
