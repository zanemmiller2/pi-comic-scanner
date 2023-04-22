"""
Author: Zane Miller
Adapted From: https://github.com/sparkfun/DE2120_Py/blob/main/examples/de2120_ex1_serial_scan.py
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
            "\t(3) Quit\n: "
            )

        if start_res == '1':
            self.lookup_comics_by_barcode()
        elif start_res == '2':
            self.lookup_creators()
        elif start_res == '3':
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

        # 1) Lookup each barcode and save as ComicBook Object
        print("Creating Creator() for each creatorid")
        for creator in self.lookup.creators:
            self.lookup.lookup_marvel_creator_by_id(creator)

        # 2) Upload each ComicBook() to database
        print("Uploading Creators()s to database")
        for creator in self.lookup.creators:
            if self.lookup.creators[creator] is not None:
                self.lookup.update_complete_creator(creator)
            else:
                print(f"SELF.LOOKUP.CREATORS[{creator}] HAS NO Creator() OBJECT")

        print("UPLOADED THE FOLLOWING COMIC BOOKS")
        self.lookup.print_committed_barcodes()

        print("CLEANING UP COMMITTED COMICS FROM scanned_upc_codes")
        self.lookup.remove_committed_from_buffer_db()

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
