"""
Author: Zane Miller
Adapted From: https://github.com/sparkfun/DE2120_Py/blob/main/examples/de2120_ex1_serial_scan.py
Email: millerzanem@gmail.com
Date: 04/15/2023
Description: Command Line interface driver
"""

from scanner_driver import *

SCANNER_INPUT_MODE = '1'
KEYBOARD_INPUT_MODE = '2'
QUIT_INPUT_MODE = '3'
MENU_NAV_MODE = '4'


class UI:
    """ UI Driver class that handles menu navigation and control functions """

    def __init__(self):
        """
        UI Object with input method (scanner, keyboard, etc) and an serial port
        entry_cursor if scanner mode active
        """
        self.input_method = None
        self.entry_cursor = None

    ####################################################
    #               NAVIGATION MENU
    ####################################################
    def get_menu_nav(self) -> int:
        """
        Asks the user which menu they would like to return to.
        :return: Returns menu option if valid otherwise asks again.
        """

        if self.entry_cursor is None:
            self.ask_scan_mode()

        if self.entry_cursor.get_num_barcodes() > 0:
            num_menu_options = 3
            print(
                "What would you like to do?"
                "\n\t(1) Scan"
                "\n\t(2) Review"
                "\n\t(3) Upload To Database"
                "\n\t(Q) Quit"
            )
        else:
            num_menu_options = 1
            print(
                "What would you like to do?"
                "\n\t(1) Scan"
                "\n\t(Q) Quit"
            )

        menu_res = input(">>> ").strip()

        if menu_res.isnumeric():
            if int(menu_res) < 1 or int(menu_res) > num_menu_options:
                print("Invalid option...")
                return self.get_menu_nav()

            if menu_res == '1':
                self.ask_scan_mode()
            elif menu_res == '2':
                self.ask_review()
            elif menu_res == '3':
                self.ask_db_upload()

        elif menu_res == "Q" or menu_res == 'q':
            self.exit_program()


        else:
            print("Invalid option...")
            return self.get_menu_nav()

    ####################################################
    #               SCAN MENU
    ####################################################
    def ask_scan_mode(self):
        """
        Asks the user what mode they would like to enter barcodes
        """
        while self.input_method != SCANNER_INPUT_MODE and self.input_method != KEYBOARD_INPUT_MODE and self.input_method != QUIT_INPUT_MODE:
            print(
                f"How would you like to upload barcodes?"
                f"\n\t({SCANNER_INPUT_MODE}) Barcode Scanner"
                f"\n\t({KEYBOARD_INPUT_MODE}) Keyboard Entry"
                f"\n\t({MENU_NAV_MODE}) Return to Navigation Menu"
                f"\n\t({QUIT_INPUT_MODE}) Quit"
            )
            self.input_method = input(">>> ").strip()

            # Scanner
            if self.input_method == SCANNER_INPUT_MODE:
                self.entry_cursor = ScannerBarcodeEntry(device_driver="/dev/cu.usbmodem141101")

            # Keyboard
            elif self.input_method == KEYBOARD_INPUT_MODE:
                self.entry_cursor = KeyboardBarcodeEntry()

            # Quit
            elif self.input_method == QUIT_INPUT_MODE:
                self.entry_cursor = None
                self.exit_program()

            # Go to Navigation Menu
            elif self.input_method == MENU_NAV_MODE:
                self.get_menu_nav()

            # Invalid Input
            else:
                print("Invalid Entry")

        self.entry_cursor.enter_marvel_barcodes()
        self.get_menu_nav()

    ####################################################
    #               REVIEW MENU
    ####################################################
    def ask_review(self):
        """
        Asks the user if they would like to review the barcodes they scanned in
        """
        review_res = ""
        while review_res.upper() != "N" and self.entry_cursor.get_num_barcodes() > 0:
            review_res = input("Would you like to review your entries (y/n)?: ")

            # Review
            if review_res.upper() == "Y":
                self.entry_cursor.review_barcodes()
                self.get_menu_nav()

            # Return to Navigation Menu
            elif review_res.upper() == "N":
                self.get_menu_nav()

                # Invalid Entry
            else:
                print("Invalid entry...")

        # Nothing to review - Exit()
        if self.entry_cursor.get_num_barcodes() == 0:
            print("Nothing left to review...")
            self.exit_program()

    ####################################################
    #               DB UPLOAD MENU
    ####################################################
    def ask_db_upload(self):
        """
        Asks the user if they want to upload comics to database.
        """
        if self.entry_cursor.get_num_barcodes() > 0:
            print("Would you like to upload the scanned barcodes to the database (y/n)? ")
            db_upload_res = input(">>> ").strip()

            if db_upload_res == 'N' or db_upload_res == 'n':
                self.get_menu_nav()
            elif db_upload_res == 'Y' or db_upload_res == 'y':
                self.entry_cursor.upload_db()
                self.get_menu_nav()

            else:
                print("Invalid entry...")
                self.ask_db_upload()

        else:
            print("No barcodes to upload.")
            self.get_menu_nav()

    ####################################################
    #                   UTILITIES
    ####################################################
    @staticmethod
    def exit_program():
        """
        Prints exit message and quits
        """
        print("Exiting...")
        exit(1)


if __name__ == '__main__':
    ui = UI()
    ui.get_menu_nav()
