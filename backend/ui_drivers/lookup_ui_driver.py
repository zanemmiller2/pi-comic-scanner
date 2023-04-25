"""
Author: Zane Miller
Email: millerzanem@gmail.com
Date: 04/15/2023
Description: Command Line interface driver
"""

from backend.classes.lookup_driver import Lookup
from backend.database.db_driver import DB


class LookupUI:
    """ UI Driver class that handles menu navigation and control functions """

    def __init__(self):
        """
        LookupUI Object with db and lookup object
        scanner if scanner mode active
        """
        self.db = DB()  # DB object controller passed to Lookup class
        self.lookup = Lookup(self.db)  # lookup controller

    ####################################################################################################################
    #
    #               NAVIGATION MENU
    #
    ####################################################################################################################

    def start_menu(self):
        """
        Initial start up menu asks user if they want to get the barcodes from the database to lookup
        """
        start_res = input(
            "Would you like to:\n"
            "\t(1) Lookup barcodes\n"
            "\t(2) Update Creators records\n"
            "\t(3) Update Series records\n"
            "\t(4) Update Story records\n"
            "\t(5) Quit\n: "
            )

        if start_res == '1':
            self.lookup_comics_by_barcode()
        elif start_res == '2':
            self.lookup_creators()
        elif start_res == '3':
            self.lookup_series()
        elif start_res == '4':
            self.lookup_stories()
        elif start_res == '5':
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

    def lookup_comics_by_barcode(self):
        """
        Lookup barcodes from the available barcodes in the scanned_upc_codes db table
        """

        self.lookup.get_barcodes_from_db()

        if self.lookup.get_num_queued_barcodes() == 0:
            print("NOTHING TO LOOKUP...GOODBYE")
            self.exit_program()
        else:
            self.process_comics()

    def process_comics(self):
        """
        Processes comics
        """
        print("SUCCESSFULLY GOT BARCODES FROM scanned_upc_codes")
        self.lookup.print_queued_barcodes()

        # 1) Lookup each barcode and save as ComicBook Object
        print("Creating ComicBook() for each barcode")
        for barcode in self.lookup.queued_barcodes:
            self.lookup.lookup_marvel_comic_by_upc(barcode)

        # 2) Upload each ComicBook() to database
        print("Uploading ComicBook()s to database")
        for barcode in self.lookup.lookedUp_barcodes:
            self.lookup.upload_comic_book(barcode)

        print("UPLOADED THE FOLLOWING COMIC BOOKS")
        self.lookup.print_committed_barcodes()

        print("CLEANING UP COMMITTED COMICS FROM scanned_upc_codes")
        self.lookup.remove_committed_from_buffer_db()

    ####################################################################################################################
    #
    #               CREATORS
    #
    ####################################################################################################################
    def lookup_creators(self):
        """
        Updates the creator records that already exist in the database
        """
        self.lookup.get_stale_creators_from_db()

        if self.lookup.get_num_stale_creators() == 0:
            print("NOTHING TO LOOKUP...GOODBYE")
            self.exit_program()
        else:
            self.process_creators()

    def process_creators(self):
        """
        Processes Creators
        """
        print("SUCCESSFULLY GOT STALE CREATORS FROM Creators")

        # 1) Lookup each stale creator and save as Creator() Object
        print("Creating Creator() for each creatorid")
        for creator in self.lookup.creators:
            self.lookup.lookup_marvel_creator_by_id(creator)

        # 2) Upload each Creator() to database
        print("Uploading Creators()s to database")
        for creator in self.lookup.creators:
            if self.lookup.creators[creator] is not None:
                self.lookup.update_complete_creator(creator)
            else:
                print(f"SELF.LOOKUP.CREATORS[{creator}] HAS NO Creator() OBJECT")

        print("UPLOADED THE FOLLOWING Creators")
        self.lookup.print_creator_ids()

    ####################################################################################################################
    #
    #               SERIES
    #
    ####################################################################################################################
    def lookup_series(self):
        """
        Updates the series records that already exist in the database
        """
        self.lookup.get_stale_series_from_db()

        if self.lookup.get_num_stale_series() == 0:
            print("NOTHING TO LOOKUP...GOODBYE")
            self.exit_program()
        else:
            self.process_series()

    def process_series(self):
        """
        Processes Series
        """
        print("SUCCESSFULLY GOT STALE SERIES FROM Series")

        # 1) Lookup each stale series
        print("Creating Series() for each seriesId")
        for series in self.lookup.series:
            self.lookup.lookup_marvel_series_by_id(series)

        # 2) Upload each Series() to database
        print("Uploading Series() to database")
        for series in self.lookup.series:
            if self.lookup.series[series] is not None:
                self.lookup.update_complete_series(series)
            else:
                print(f"SELF.LOOKUP.SERIES[{series}] HAS NO Series() OBJECT")

        print("UPLOADED THE FOLLOWING SERIES")
        self.lookup.print_series_ids()

    ####################################################################################################################
    #
    #               STORIES
    #
    ####################################################################################################################
    def lookup_stories(self):
        """
        Updates the Stories records that already exist in the database
        """
        self.lookup.get_stale_stories_from_db()

        if self.lookup.get_num_stale_stories() == 0:
            print("NOTHING TO LOOKUP...GOODBYE")
            self.exit_program()
        else:
            self.process_stories()

    def process_stories(self):
        """
        Processes Series
        """
        print("SUCCESSFULLY GOT STALE STORIES FROM Stories")

        # 1) Lookup each stale story
        print("Creating Story() for each storyId")
        for story in self.lookup.stories:
            self.lookup.lookup_marvel_story_by_id(story)

        # 2) Upload each Story() to database
        print("Uploading Story() to database")
        for story in self.lookup.stories:
            if self.lookup.stories[story] is not None:
                self.lookup.update_complete_story(story)
            else:
                print(f"SELF.LOOKUP.STORIES[{story}] HAS NO Story() OBJECT")

        print("UPLOADED THE FOLLOWING STORIES")
        self.lookup.print_story_ids()

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
        print("CLOSING LOOKUP UI DB CURSOR...")
        self.db.close_cursor()
        print("QUITTING LOOKUP UI PROGRAM...")
        exit(1)


if __name__ == '__main__':
    lookup_ui = LookupUI()
    lookup_ui.start_menu()
