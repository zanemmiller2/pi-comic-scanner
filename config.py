import keys.db_credentials
import keys.private_keys


class Config:
    MYSQL_HOST = keys.db_credentials.host
    MYSQL_USER = keys.db_credentials.user
    MYSQL_PASSWORD = keys.db_credentials.passwd
    MYSQL_DB = keys.db_credentials.db
    MYSQL_CURSORCLASS = 'DictCursor'
    SECRET_KEY = keys.private_keys.secret_key
