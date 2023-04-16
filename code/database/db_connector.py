import MySQLdb


# Set the variables in our application with those environment variables

def connect_to_database():
    """
    connects to a database and returns a database objects
    """
    host = input("DB Host: ")
    user = input("DB User: ")
    passwd = input("DB Password: ")
    db = input("DB Name: ")
    db_connection = MySQLdb.connect(host, user, passwd, db)
    return db_connection


def upload_upc_to_buffer(db_connection=None, query_params=(str, str)):
    """
    Uploads a tuple of strings (upc and YYYY-MM-DD) to the scanned_upc_codes table in the comic_books database
    :param db_connection: db_connection object
    :param query_params: (upc: str, YYYY-MM-DD: str)
    :return: cursor object from connection
    """

    if db_connection is None:
        print(
            "No connection to the database found! Have you called connect_to_database() first?"
        )
        return None

    query = "INSERT INTO comic_books.scanned_upc_codes(upc_code, date_uploaded) VALUES (%s, %s);"

    print("Executing %s with %s" % (query, query_params))
    # Create a cursor to execute query. Why? Because apparently they optimize execution by retaining a reference according to PEP0249
    cursor = db_connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(query, query_params)

    return cursor
