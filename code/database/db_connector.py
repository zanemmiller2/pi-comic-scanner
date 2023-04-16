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


def execute_query(db_connection=None, query=None, query_params=()):
    """
    executes a given SQL query on the given db connection and returns a Cursor object

    db_connection: a MySQLdb connection object created by connect_to_database()
    query: string containing SQL query

    returns: A Cursor object as specified at https://www.python.org/dev/peps/pep-0249/#cursor-objects.
    You need to run .fetchall() or .fetchone() on that object to actually acccess the results.

    """

    if db_connection is None:
        print(
            "No connection to the database found! Have you called connect_to_database() first?"
        )
        return None

    if query is None or len(query.strip()) == 0:
        print("query is empty! Please pass a SQL query in query")
        return None

    print("Executing %s with %s" % (query, query_params))
    # Create a cursor to execute query. Why? Because apparently they optimize execution by retaining a reference according to PEP0249
    cursor = db_connection.cursor(MySQLdb.cursors.DictCursor)
    parameters = query_params
    cursor.execute(query, parameters)
    # this will actually commit any changes to the database. without this no
    # changes will be committed!
    return cursor


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
