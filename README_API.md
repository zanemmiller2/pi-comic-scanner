# 1. **Function Descriptions**

<!-- TOC -->

* [1. **Function Descriptions**](#1-function-descriptions)
    * [**1. Lookup()**](#1-lookup)
    * [**2. Scanner()**](#2-scanner)
    * [**3. ScannerBarcodeEntry(
      Scanner)**](#3-scannerbarcodeentryscanner-required-db_connection-dbconnection-required-device_driver-str-optional-baud_rate-int--115200-optional-timeout-int--1)
    * [**4. KeyboardBarcodeEntry(
      Scanner)**](#4-keyboardbarcodeentryscanner-required-db_connection-dbconnection)
    * [**5. DB()**](#5-db)
    * [**6. Scanner UI**](#6-scanner-ui)
    * [**7. Lookup UI**](#7-lookup-ui)

<!-- TOC -->

### **1. Lookup()**

1. **Http Interactions**
    1. **Lookup.lookup_marvel_by_upc(barcode: str):**
        1. Sends the http request
           to https://gateway.marvel.com/v1/public/comics endpoint and stores
           response as ComicBook() object.
2. **Lookup() -> ComicBook() Interactions**
    1. **Lookup.upload_comic_book(barcode: str):**
        1. Create a new database record for the looked up comic book. First
           uploads any non-existent foreign key dependencies and then uploads
           the entire comic_book object.
3. **Lookup() -> Database Interactions**
    1. **Lookup.get_barcodes_from_db():**
        1. Queries the database for any queued_barcodes in the
           scanned_upc_codes table.
        2. Saves the barcodes from the scanned_upc_codes table as a dictionary
           of queued_barcodes[barcode] = {'prefix': upc_prefix, 'upload_date':
           upload_date}
    2. **Lookup.remove_committed_from_buffer_db():**
        1. Deletes the barcodes that have been committed to the database from
           the scanned_upc_codes table.
        2. Function removes barcodes from committed_barcodes dictionary.
4. **Getters and Setters**
    1. **Lookup.get_num_queued_barcodes() -> int:**
        1. Gets the number of barcodes ready for api lookup.
        2. These barcodes have not been looked up yet. This is the queuing
           stage.
    2. **Lookup.get_num_lookedUp_barcodes() -> int:**
        1. Gets the number of barcodes that have already been queried and
           stored as a comic book object.
        2. These barcodes are waiting to be committed to the comic book
           database.
    3. **Lookup.get_num_committed_barcodes() -> int:**
        1. Gets the number of barcodes that have already been queried, stored,
           and committed to the database.
        2. These barcodes are completely done and can be deleted from the
           scanned_upc_codes database.
    4. **Lookup.print_queued_barcodes():**
        1. Prints the formatted list of barcodes in the queued_barcodes
           dictionary
    5. **Lookup.print_lookedUp_barcodes():**
        1. Prints the formatted list of barcodes in the lookedUp_barcodes
           dictionary
    6. **Lookup.print_committed_barcodes():**
        1. Prints the formatted list of barcodes in the committed_barcodes
           dictionary
5. **Utilities**
    1. **Lookup.quit_program():**
        1. Confirms user wants to quit if there are still barcodes in the
           queue.
        2. Removes committed barcodes from the scanned_upc_codes table before
           exit(1)

### **2. Scanner()**

1. **Review**
    1. **Scanner.review_barcodes():**
        1. UI Interface for reviewing the latest entry and asks the user if
           they want to make any modifications.
2. **Scanner() -> Database Interactions**
    1. **Scanner.upload_db():**
        1. Uploads scanned upcs to database
3. **Getters and Setters**
    1. **Scanner.get_num_barcodes() -> int:**
        1. Gets the number of barcodes in the scanned list.
    2. **Scanner.get_entry_method():**
        1. Returns the current entry_mode (scanner, keyboard) for inputting
           barcodes.
4. **Parent Utilities**
    1. **Scanner.get_formatted_YYYY_MM_DD_string() -> str:**
        1. Returns the current time as a string in YYYY-MM-DD format
    2. **Scanner.format_marvel_barcode(mav18_barcode: str) -> str:**
        1. Formats the current 18 digit upc code by appending the 'MAV18-'
           prefix to the barcode. Returns the formatted input string.

### **3. ScannerBarcodeEntry(Scanner)**

1. ScannerBarcodeEntry(Scanner, required db_connection: db.connection, required
   device_driver: str, optional baud_rate: int = 115200, optional timeout: int
   = 1)
2. Inherits from Scanner parent class.
3. Modifies **Scanner.enter_marvel_barcodes():**
    1. Reads marvel _barcodes (UPC-A with a 5-digit add_on code) from
       serial_scanner with a 5 digit add on code. The first 3 digits of the
       add-on code represent the issue number, the 4th digit represents the
       cover variant and the 5th digit represents the print variant.

### **4. KeyboardBarcodeEntry(Scanner)**

1. KeyboardBarcodeEntry(Scanner, required db_connection: db.connection)
1. Inherits from Scanner parent class.
2. Modifies **Scanner.enter_marvel_barcodes():**
    1. Reads marvel _barcodes (UPC-A with a 5-digit add_on code) from user
       keyboard input with a 5 digit add on code. The first 3 digits of the
       add-on code represent the issue number, the 4th digit represents the
       cover variant and the 5th digit represents the print variant.

### **5. DB()**

1. **Pull From Database**
    1. **DB.get_upcs_from_buffer():**
        1. Selects all entries from scanned_upc_codes from comic_books database
           returns cursor.fetchall()
2. **Upload To Database**
    1. **DB.upload_upc_to_buffer(query_params: tuple[str, str]):**
        1. Uploads a tuple of strings (upc and YYYY-MM-DD) to the
           scanned_upc_codes table in the comic_books database.
    2. **DB.upload_new_comic_book(params: tuple):**
        1. Takes a tuple of comic_book properties from ComicBook() object and
           inserts a new comic book record in the comic_books.comics table
    3. **DB.upload_new_image_record(full_image_path: str):**
        1. Uploads a new image path to comic_books.image_paths if image path
           does not already exist in database
    4. **DB.upload_new_url_record(url_type: str, url_path: str):**
        1. Uploads a new url record to comic_books.URLs if URL does not already
           exist in database
    5. **DB.upload_new_creator_record(creator_id: int, first_name: str,
       middle_name: str, last_name: str, resource_uri: str):**
        1. Uploads a new creator record with id, first name, middle name, last
           name, and resourceURI to comic_books.creators if Creator does not
           already exist in database
    6. **DB.upload_new_character_record(character_id: int, character_name: str,
       resource_uri: str):**
        1. Uploads a new character record with character id, character name,
           and character resource uri to comic_books.characters if URL does not
           already exist in database.
    7. **DB.upload_new_story_record(story_id: int, story_title: str,
       resource_uri: str, story_type: uri):**
        1. Uploads a new story record with story id, title, uri, and type to
           comic_books.stories if story does not already exist in database.
    8. **DB.upload_new_record_by_table(table_name: str, entity_id: int,
       entity_title: str, entity_uri: str):**
        1. Generic function that works the same for the Events, Series, and
           Variant("Comics") entity. Each of these 3 entities is upload with
           the same properties by the same name.
        2. Uploads a new record to comic_books.table_name (Events, Series, or "
           Variant (Comics) if record does not already exist in database using
           id, title, and uri.
3. **Add New Comics_Has_Relationships**
    1. **DB.upload_new_comics_has_creators_record(comic_id: int, creator_id:
       int, creator_role: str):**
        1. Creates a new Comics_has_Creators record if the comic_id and
           character_id aren't already related with the creator_role
    2. **DB.upload_new_comics_has_images_record(comid_id: int, image_path:
       str):**
        1. Creates a new Comics_has_Creators record if the comic_id and
           image_path aren't already related
    3. **DB.upload_new_comics_has_urls_record(comic_id: int, url: str):**
        1. Creates a new Comics_has_Stories record if the comic_id and story_id
           aren't already related.
    4. **DB.upload_new_comics_has_characters_record(comic_id: int,
       character_id: int):**
        1. Creates a new Comics_has_Characters record if the comic_id and
           character_id aren't already related.
    5. **DB.upload_new_comics_has_events_record(comic_id: int, event_id:
       int):**
        1. Creates a new Comics_has_Events record if the comic_id and event_id
           aren't already related.
    6. **DB.upload_new_comics_has_stories_record(comic_id: int, story_id:
       int):**
        1. Creates a new Comics_has_Stories record if the comic_id and story_id
           aren't already related.
    7. **DB.upload_new_comics_has_variants_record(comic_id: int, variant_id:
       int):**
        1. Creates a new Comics_has_Stories record if the comic_id and story_id
           aren't already related
4. **Delete Records from DB**
    1. **DB.delete_from_scanned_upc_codes_table(upc_code: str):**
        1. Function deletes records from the scanned_upc_codes table based on
           the upc_code with appended prefix provided.

### **6. Scanner UI**

1. The Scanner UI and Lookup UI are temporary middleware for local development
   testing. These will be converted to a web based UI and primarily serve for
   testing and outlining and refining the desired algorithmic flow of the
   program.
2. The primary function of the scanner UI is to query user for responses and
   direct the flow of the Scanner class.
    1. Asks the user the mode of entry (Scanner or Keyboard)
    2. Takes in barcode entries either through the keyboard or scanner and
       stores them in a data structure.
    3. Assists the user in reviewing scanned barcodes and making any changes.
    4. Assists the user in uploading scanned barcodes to the
       comic_books.scanned_upc_codes table.

### **7. Lookup UI**

1. The Scanner UI and Lookup UI are temporary middleware for local development
   testing. These will be converted to a web based UI and primarily serve for
   testing and outlining and refining the desired algorithmic flow of the
   program.
2. The primary function of the Lookup UI right now is to provide a command line
   interface for automatically:
    1. Pulling barcodes from the scanned_upc_codes table,
    2. Lookup barcodes using Marvel's public API
    3. Parse the Marvel API json response data by Creating ComicBook() objects
       for each upc code in the scanned_upc_codes table that was successfully
       looked up with the Marvel API.
    4. Creating any new non-existent foreign key dependencies that Comics
       entity relies on (seriesId, thumbnail, originalIssue).
    5. Uploading the ComicBook() to the database with its complete data
    6. Creating the Many:Many intersection table records that rely on the
       Comics.id and the relevant foreign keys from other tables. 
