"""
Author: Zane Miller
Adapted From: https://github.com/sparkfun/DE2120_Py/blob/main/examples/de2120_ex1_serial_scan.py
Email: millerzanem@gmail.com
Date: 04/15/2023
Description: Command Line interface driver
"""
from database import db_driver as db
from lookup_driver import Lookup


class LookupUI:
    """ UI Driver class that handles menu navigation and control functions """

    def __init__(self):
        """
        UI Object with input method (scanner, keyboard, etc) and an serial port
        entry_cursor if scanner mode active
        """
        self.db_cursor = db.connect_to_database()
        self.lookup_cursor = Lookup(self.db_cursor)

    ####################################################
    #               NAVIGATION MENU
    ####################################################
    def get_menu_nav(self) -> int:
        """
        Asks the user which menu they would like to return to.
        :return: Returns menu option if valid otherwise asks again.
        """

        if self.lookup_cursor.get_num_barcodes() == 0:
            num_menu_options = 1
            print(
                "What would you like to do?"
                "\n\t(1) Pull Barcodes from scanned_upc_codes table"
                "\n\t(Q) Quit"
            )
        else:
            num_menu_options = 2
            print(
                "What would you like to do?"
                "\n\t(1) Pull Barcodes from scanned_upc_codes table"
                "\n\t(2) Lookup Barcodes (API)"
                "\n\t(Q) Quit"
            )

        menu_res = input(">>> ").strip()

        if menu_res.isnumeric():
            if int(menu_res) < 1 or int(menu_res) > num_menu_options:
                print("Invalid option...")
                return self.get_menu_nav()

            if menu_res == '1':
                self.lookup_cursor.get_barcodes_from_db()
            elif menu_res == '2':
                self.lookup_cursor.lookup_marvel_by_upc()

        elif menu_res == "Q" or menu_res == 'q':
            self.exit_program()


        else:
            print("Invalid option...")
            return self.get_menu_nav()

    ####################################################
    #                   UTILITIES
    ####################################################
    def exit_program(self):
        """
        Prints exit message and quits
        """
        self.db_cursor.close()
        print("Exiting...")
        exit(1)


if __name__ == '__main__':
    lookup_ui = LookupUI()
    lookup_ui.get_menu_nav()
