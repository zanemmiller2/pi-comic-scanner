"""
Author: Zane Miller
Adapted From: https://github.com/sparkfun/DE2120_Py/blob/main/examples/de2120_ex1_serial_scan.py
Email: millerzanem@gmail.com
Date: 04/15/2023
Description: Command Line interface driver
"""

from code.classes.lookup_driver import Lookup
from code.database.db_driver import DB


class LookupUI:
    """ UI Driver class that handles menu navigation and control functions """

    def __init__(self):
        """
        LookupUI Object with db and lookup object
        scanner if scanner mode active
        """
        self.db = DB()  # DB object controller passed to Lookup class
        self.lookup = Lookup(self.db)  # lookup controller

    ####################################################
    #               NAVIGATION MENU
    ####################################################

    def start_menu(self):
        """
        Initial start up menu asks user if they want to get the barcodes from the database to lookup
        """
        start_res = input("Would you like to begin looking up barcodes (y/n)? ")

        if start_res == 'y' or start_res == 'Y':
            self.lookup.get_barcodes_from_db()

            if self.lookup.get_num_queued_barcodes() == 0:
                print("NOTHING TO LOOKUP...GOODBYE")
                self.exit_program()
            else:
                self.process_barcodes()

        elif start_res == 'n' or start_res == 'N':
            print("NOTHING FOR ME TO DO THEN...GOODBYE")
            self.exit_program()

        else:
            print("INVALID RESPONSE...RETURNING TO THE START MENU")
            self.start_menu()

    def process_barcodes(self):
        """
        Processes barcodes
        """
        print("SUCCESSFULLY GOT BARCODES FROM scanned_upc_codes")
        self.lookup.print_queued_barcodes()

        # 1) Lookup each barcode and save as ComicBook Object
        print("Creating ComicBook() for each barcode")
        for barcode in self.lookup.queued_barcodes:
            self.lookup.lookup_marvel_by_upc(barcode)

        # 2) Upload each ComicBook() to database
        print("Uploading ComicBook()s to database")
        for barcode in self.lookup.lookedUp_barcodes:
            self.lookup.upload_comic_book(barcode)

        print("UPLOADED THE FOLLOWING COMIC BOOKS")
        self.lookup.print_committed_barcodes()

        print("CLEANING UP COMMITTED COMICS FROM scanned_upc_codes")
        self.lookup.remove_committed_from_buffer_db()

    ####################################################
    #                   UTILITIES
    ####################################################
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
