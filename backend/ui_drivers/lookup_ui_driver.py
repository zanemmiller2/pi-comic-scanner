"""
Author: Zane Miller
Email: millerzanem@gmail.com
Date: 04/15/2023
Description: Command Line interface driver
"""

from backend.backendDatabase.backendDB import BackEndDB
from backend.classes.lookup_driver import Lookup


class LookupUI:
    """ UI Driver class that handles menu navigation and control functions """

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
                SERIES_ENTITY, STORY_ENTITY, URL_ENTITY, PURCHASED_COMICS_ENTITY, VARIANT_ENTITY)

    def __init__(self):
        """
        LookupUI Object with db and lookup object
        scanner if scanner mode active
        """
        self.db = BackEndDB()  # BackEndDB object controller passed to Lookup class
        self.lookup = Lookup(self.db)  # lookup controller

    ####################################################################################################################
    #
    #               NAVIGATION MENU
    #
    ####################################################################################################################

    def start_menu(self):
        """
        Initial start up menu asks user if they want to get the barcodes from the backendDatabase to lookup
        """
        start_res = input(
            "Would you like to:\n"
            "\t(1) Lookup barcodes\n"
            "\t(2) Update Creators records\n"
            "\t(3) Update Series records\n"
            "\t(4) Update Story records\n"
            "\t(5) Update Character records\n"
            "\t(6) Update Event records\n"
            "\t(7) Update Comic records\n"
            "\t(8) Update Purchased Comics and Their Dependencies\n"
            "\t(9) Quit\n: "
        )

        if start_res == '1':
            self.get_comic_barcodes()
        elif start_res == '2':
            self.lookup_existing_creators()
        elif start_res == '3':
            self.lookup_existing_series()
        elif start_res == '4':
            self.lookup_existing_stories()
        elif start_res == '5':
            self.lookup_existing_characters()
        elif start_res == '6':
            self.lookup_existing_events()
        elif start_res == '7':
            self.lookup_existing_comics_by_id()
        elif start_res == '8':
            self.lookup_purchased_comics_dependencies()
        elif start_res == '9':
            print("NOTHING FOR ME TO DO THEN...GOODBYE")
            self.exit_program()
        else:
            print("INVALID RESPONSE...RETURNING TO THE START MENU")
            self.start_menu()

    ####################################################################################################################
    #
    #               COMICS
    #
    ####################################################################################################################

    def get_comic_barcodes(self):
        """
        Lookup barcodes from the available barcodes in the scanned_upc_codes db table
        """

        self.lookup.get_barcodes_from_db()

        if self.lookup.get_num_queued_barcodes() == 0:
            print("NOTHING TO LOOKUP...GOODBYE")
            self.exit_program()
        else:
            print("SUCCESSFULLY GOT BARCODES FROM scanned_upc_codes")
            self.process_comics_by_barcode()

    def process_comics_by_barcode(self):
        """
        Processes comics
        """
        self.lookup.print_queued_barcodes()

        # 1) Lookup each barcode and save as ComicBook Object
        print("Creating ComicBook() for each barcode")
        for barcode in self.lookup.queued_barcodes:
            self.lookup.lookup_marvel_comic_by_upc(barcode)

        # 2) Upload each ComicBook() to backendDatabase
        print("Uploading ComicBook()s to backendDatabase")
        for barcode in self.lookup.lookedUp_barcodes:
            self.lookup.upload_complete_comic_book_byUPC(barcode)

        print("UPLOADED THE FOLLOWING COMIC BOOKS")
        self.lookup.print_committed_barcodes()

        print("CLEANING UP COMMITTED COMICS FROM scanned_upc_codes")
        self.lookup.remove_committed_from_buffer_db()

    def lookup_existing_comics_by_id(self):
        """
        Updates the Comic records that already exist in the backendDatabase
        """
        self.lookup.get_stale_entity_from_db(self.COMIC_ENTITY)

        if self.lookup.get_num_entity(self.COMIC_ENTITY) == 0:
            print("NOTHING TO LOOKUP...GOODBYE")
            self.exit_program()
        else:
            print("SUCCESSFULLY GOT STALE COMICS FROM Comics")
            self.process_comics_by_id()

    def process_comics_by_id(self):
        """
        Processes Comics by ID
        """
        # 1) Lookup each stale comic and save as Comic() Object
        print("Creating Comic() for each comicId")
        for comic in self.lookup.comic_books:
            self.lookup.lookup_marvel_comic_by_id(comic)

        # 2) Upload each COmic() to backendDatabase
        print("Uploading Comic()s to backendDatabase")
        for comic in self.lookup.comic_books:
            if self.lookup.comic_books[comic] is not None:
                self.lookup.update_complete_comic_book_byID(comic)
            else:
                print(f"SELF.LOOKUP.COMICS[{comic}] HAS NO Comic() OBJECT")

        print("UPLOADED THE FOLLOWING Comics")
        self.lookup.print_entity_ids(self.COMIC_ENTITY)

    ####################################################################################################################
    #
    #               CREATORS
    #
    ####################################################################################################################
    def lookup_existing_creators(self):
        """
        Updates the creator records that already exist in the backendDatabase
        """
        self.lookup.get_stale_entity_from_db(self.CREATOR_ENTITY)

        if self.lookup.get_num_entity(self.CREATOR_ENTITY) == 0:
            print("NOTHING TO LOOKUP...GOODBYE")
            self.exit_program()
        else:
            print("SUCCESSFULLY GOT STALE CREATORS FROM Creators")
            self.process_creators()

    def process_creators(self):
        """
        Processes Creators
        """
        # 1) Lookup each stale creator and save as Creator() Object
        print("Creating Creator() for each creatorId")
        for creator in self.lookup.creators:
            self.lookup.lookup_marvel_creator_by_id(creator)

        # 2) Upload each Creator() to backendDatabase
        print("Uploading Creators()s to backendDatabase")
        for creator in self.lookup.creators:
            if self.lookup.creators[creator] is not None:
                self.lookup.update_complete_creator(creator)
            else:
                print(f"SELF.LOOKUP.CREATORS[{creator}] HAS NO Creator() OBJECT")

        print("UPLOADED THE FOLLOWING Creators")
        self.lookup.print_entity_ids(self.CREATOR_ENTITY)

    ####################################################################################################################
    #
    #               SERIES
    #
    ####################################################################################################################
    def lookup_existing_series(self):
        """
        Updates the series records that already exist in the backendDatabase
        """
        self.lookup.get_stale_entity_from_db(self.SERIES_ENTITY)

        if self.lookup.get_num_entity(self.SERIES_ENTITY) == 0:
            print("NOTHING TO LOOKUP...GOODBYE")
            self.exit_program()
        else:
            print("SUCCESSFULLY GOT STALE SERIES FROM Series")
            self.process_series()

    def process_series(self):
        """
        Processes Series
        """
        # 1) Lookup each stale series
        print("Creating Series() for each seriesId")
        for series in self.lookup.series:
            self.lookup.lookup_marvel_series_by_id(series)

        # 2) Upload each Series() to backendDatabase
        print("Uploading Series() to backendDatabase")
        for series in self.lookup.series:
            if self.lookup.series[series] is not None:
                self.lookup.update_complete_series(series)
            else:
                print(f"SELF.LOOKUP.SERIES[{series}] HAS NO Series() OBJECT")

        print("UPLOADED THE FOLLOWING SERIES")
        self.lookup.print_entity_ids(self.SERIES_ENTITY)

    ####################################################################################################################
    #
    #               STORIES
    #
    ####################################################################################################################
    def lookup_existing_stories(self):
        """
        Updates the Stories records that already exist in the backendDatabase
        """
        self.lookup.get_stale_entity_from_db(self.STORY_ENTITY)

        if self.lookup.get_num_entity(self.STORY_ENTITY) == 0:
            print("NOTHING TO LOOKUP...GOODBYE")
            self.exit_program()
        else:
            print("SUCCESSFULLY GOT STALE STORIES FROM Stories")
            self.process_stories()

    def process_stories(self):
        """
        Processes Series
        """
        # 1) Lookup each stale story
        print("Creating Story() for each storyId")
        for story in self.lookup.stories:
            self.lookup.lookup_marvel_story_by_id(story)

        # 2) Upload each Story() to backendDatabase
        print("Uploading Story() to backendDatabase")
        for story in self.lookup.stories:
            if self.lookup.stories[story] is not None:
                self.lookup.update_complete_story(story)
            else:
                print(f"SELF.LOOKUP.STORIES[{story}] HAS NO Story() OBJECT")

        print("UPLOADED THE FOLLOWING STORIES")
        self.lookup.print_entity_ids(self.STORY_ENTITY)

    ####################################################################################################################
    #
    #               CHARACTERS
    #
    ####################################################################################################################
    def lookup_existing_characters(self):
        """
        Updates the Characters records that already exist in the backendDatabase
        """
        self.lookup.get_stale_entity_from_db(self.CHARACTER_ENTITY)

        if self.lookup.get_num_entity(self.CHARACTER_ENTITY) == 0:
            print("NOTHING TO LOOKUP...GOODBYE")
            self.exit_program()
        else:
            print("SUCCESSFULLY GOT STALE CHARACTERS FROM Characters")
            self.process_characters()

    def process_characters(self):
        """
        Processes Character
        """
        # 1) Lookup each stale character
        print("Creating Character() for each characterId")
        for character in self.lookup.characters:
            self.lookup.lookup_marvel_character_by_id(character)

        # 2) Upload each Character() to backendDatabase
        print("Uploading Character() to backendDatabase")
        for character in self.lookup.characters:
            if self.lookup.characters[character] is not None:
                self.lookup.update_complete_character(character)
            else:
                print(f"SELF.LOOKUP.CHARACTERS[{character}] HAS NO Character() OBJECT")

        print("UPLOADED THE FOLLOWING CHARACTERS")
        self.lookup.print_entity_ids(self.CHARACTER_ENTITY)

    ####################################################################################################################
    #
    #               EVENTS
    #
    ####################################################################################################################
    def lookup_existing_events(self):
        """
        Updates the Events records that already exist in the backendDatabase
        """
        self.lookup.get_stale_entity_from_db(self.EVENT_ENTITY)

        if self.lookup.get_num_entity(self.EVENT_ENTITY) == 0:
            print("NOTHING TO LOOKUP...GOODBYE")
            self.exit_program()
        else:
            print("SUCCESSFULLY GOT STALE EVENTS FROM Events")
            self.process_events()

    def process_events(self):
        """
        Processes Events
        """
        # 1) Lookup each stale event
        print("Creating Events() for each eventId")
        for event in self.lookup.events:
            self.lookup.lookup_marvel_event_by_id(event)

        # 2) Upload each Event() to backendDatabase
        print("Uploading Event() to backendDatabase")
        for event in self.lookup.events:
            if self.lookup.events[event] is not None:
                self.lookup.update_complete_event(event)
            else:
                print(f"SELF.LOOKUP.EVENTS[{event}] HAS NO Event() OBJECT")

        print("UPLOADED THE FOLLOWING Events")
        self.lookup.print_entity_ids(self.EVENT_ENTITY)

    ####################################################################################################################
    #
    #               VARIANTS
    #
    ####################################################################################################################

    def process_variants(self):
        """
        Processes Events
        """
        # 1) Lookup each stale comic and save as Comic() Object
        print("Creating Comic() Variant for each variantId")
        for variant in self.lookup.variants:
            self.lookup.lookup_marvel_variant_by_id(variant)

        # 2) Upload each COmic() to backendDatabase
        print("Uploading Comic()s Variants to backendDatabase")
        for variant in self.lookup.variants:
            if self.lookup.variants[variant] is not None:
                self.lookup.update_complete_variant(variant)
            else:
                print(f"SELF.LOOKUP.VARIANTS[{variant}] HAS NO Comic() OBJECT")

        print("UPLOADED THE FOLLOWING Variants")
        self.lookup.print_entity_ids(self.VARIANT_ENTITY)

    ####################################################################################################################
    #
    #               PURCHASED AND THEIR DEPENDENCIES
    #
    ####################################################################################################################
    def lookup_purchased_comics_dependencies(self):
        """
        Updates the Purchased Comics records that already exist in the backendDatabase and all its dependencies
        """

        print(f"GETTING PURCHASED COMIC IDS FROM BackendDb")
        self.lookup.get_purchased_comic_ids_from_db()
        print(
            f"SUCCESSFULLY GOT {len(self.lookup.comic_books)} "
            f"PURCHASED COMICS FROM PurchasedComics"
            )

        if self.lookup.get_num_entity(self.COMIC_ENTITY) > 0:
            self.process_comics_by_id()
            print("SUCCESSFULLY PROCESSED PURCHASED COMICS FROM Events")

            for comic_id in self.lookup.comic_books:
                print(f"GETTING {comic_id} CHARACTERS FROM BackendDb")
                self.lookup.get_comic_has_entity_ids_from_db(self.CHARACTER_ENTITY, comic_id)

                print(f"GETTING {comic_id} CREATORS FROM BackendDb")
                self.lookup.get_comic_has_entity_ids_from_db(self.CREATOR_ENTITY, comic_id)

                print(f"GETTING {comic_id} EVENTS FROM BackendDb")
                self.lookup.get_comic_has_entity_ids_from_db(self.EVENT_ENTITY, comic_id)

                print(f"GETTING {comic_id} SERIES FROM BackendDb")
                self.lookup.get_comic_has_entity_ids_from_db(self.SERIES_ENTITY, comic_id)

                print(f"GETTING {comic_id} STORIES FROM BackendDb")
                self.lookup.get_comic_has_entity_ids_from_db(self.STORY_ENTITY, comic_id)

                print(f"GETTING {comic_id} VARIANTS FROM BackendDb")
                self.lookup.get_comic_has_entity_ids_from_db(self.VARIANT_ENTITY, comic_id)

            self.process_update_purchased()

    def process_update_purchased(self):
        """
        Processes all the dependencies of a purchased comic and the comic itself
        """
        print(f"PROCESSING {len(self.lookup.characters)} CHARACTERS")
        if self.lookup.get_num_entity(self.CHARACTER_ENTITY) > 0:
            self.process_characters()

        print(f"PROCESSING {len(self.lookup.creators)} CREATORS")
        if self.lookup.get_num_entity(self.CREATOR_ENTITY) > 0:
            self.process_creators()

        print(f"PROCESSING {len(self.lookup.events)} EVENTS")
        if self.lookup.get_num_entity(self.EVENT_ENTITY) > 0:
            self.process_events()

        print(f"PROCESSING {len(self.lookup.series)} SERIES")
        if self.lookup.get_num_entity(self.SERIES_ENTITY) > 0:
            self.process_series()

        print(f"PROCESSING {len(self.lookup.stories)} STORIES")
        if self.lookup.get_num_entity(self.STORY_ENTITY) > 0:
            self.process_stories()

        print(f"PROCESSING {len(self.lookup.variants)} VARIANTS")
        if self.lookup.get_num_entity(self.VARIANT_ENTITY) > 0:
            self.process_variants()

    ####################################################################################################################
    #
    #               UTILITIES
    #
    ####################################################################################################################
    def exit_program(self):
        """
        Prints exit message and quits
        """
        self.lookup.quit_program()
        print("CLOSING LOOKUP UI BackEndDB CURSOR...")
        self.db.close_cursor()
        print("QUITTING LOOKUP UI PROGRAM...")
        exit(1)


if __name__ == '__main__':
    lookup_ui = LookupUI()
    lookup_ui.start_menu()
