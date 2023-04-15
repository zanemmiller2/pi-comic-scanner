"""
Author: Zane Miller
Adapted From: https://github.com/sparkfun/DE2120_Py/blob/main/examples/de2120_ex1_serial_scan.py
Email: millerzanem@gmail.com
Date: 04/13/2023
Description:
"""

from __future__ import print_function

import datetime
from typing import List
import de2120_barcode_scanner
import serial
import sys
import time
import database.db_connector as db


class InvalidConnectionException(Exception):
    """Raised the program cant connect to the serial port"""
    pass


class Scanner:
    """
    Scanner object to handle connecting to scanner serial port,
    scanning barcodes, and saving scanned barcodes to file
    """

    MARVEL_BARCODE_LENGTH_WITH_5DIGIT = 18

    def __init__(self):
        """
        Scanner object with hard_port, connection_status, DE2120BarcodeScanner
        serial_scanner object, and a list of scanned barcodes
        """
        self._serial_port = serial.Serial("/dev/cu.usbmodem141101", 115200, timeout=1)
        self.serial_scanner = de2120_barcode_scanner.DE2120BarcodeScanner(self._serial_port)
        self._scanner_connection_status = False
        self.scanned_barcodes_list = []
        self.db_cursor = None

        # try to connect to serial port
        try:
            self.__connect_scanner()
        except InvalidConnectionException:
            print(
                "\nThe Barcode Scanner module isn't connected correctly to the system. Please check wiring",
                file=sys.stderr
            )

    def __connect_scanner(self):
        """
        Creates a connection to the supplied serial port and saves the status
        as self._connection_status.
        """

        self._scanner_connection_status = self.serial_scanner.begin()
        if not self._scanner_connection_status:
            raise InvalidConnectionException

    def __connect_db(self):
        self.db_connection = db.connect_to_database()

    def scan_barcodes_marvel(self):
        """
        Reads marvel barcodes (UPC-A with a 5-digit add_on code) from
        serial_scanner with a 5 digit add on code. The first 3 digits of the
        add-on code represent the issue number, the 4th digit represents the
        cover variant and the 5th digit represents the print variant.
        """

        # check scanner connection status and try to reconnect if not connected
        if not self._scanner_connection_status:
            print("\nBarcode Scanner not connected. Trying to reconnect...")
            try:
                self.__connect_scanner()
            except InvalidConnectionException:
                print(
                    "\nThe Barcode Scanner module isn't connected correctly to the system. Please check wiring",
                    file=sys.stderr
                )

        # Begin Scanning
        print("Scanner ready! Begin scanning...")
        while True:
            # clear buffer before trying to read again
            barcode_buffer = self.serial_scanner.read_barcode()
            barcode_length = len(str(barcode_buffer))

            # check if a barcode was scanned
            if barcode_buffer:
                # check if the scanned barcode includes the 5 digit add on
                if barcode_length == self.MARVEL_BARCODE_LENGTH_WITH_5DIGIT:
                    print("\nCode found: " + str(barcode_buffer))
                    self.scanned_barcodes_list.append("MAV18-" + str(barcode_buffer))

                # otherwise prompt to try again
                else:
                    print("\nCould not scan the 5-digit add on code. Try again...")

                # ask the user if they have more to scan
                user_res = input("\nWould you like to scan more? (y/n): ")
                if user_res.lower() == 'n':
                    print("\nDone Scanning!")
                    break

                print("\nScan!")

            time.sleep(0.02)

    def review_barcodes(self):
        """
        Prompts user to review lines submitted for upload
        """
        delete = input("\nWould you like to remove any barcodes from the list (y/n)? : ")

        if delete.upper() == 'Y':
            self.scanned_barcodes_list = self.__delete_barcode_from_buffer_list()

        save = input(f"\nWould you like to upload the following barcodes {self.scanned_barcodes_list} (y/n)?: ")

        if save.upper() == "Y":
            print(f"\nUploading {self.scanned_barcodes_list} to database.")
            self.__upload_upcs_to_db()
        else:
            print("\nOk...deleting entry")
            self.scanned_barcodes_list = []

    def __upload_upcs_to_db(self):
        self.db_cursor = db.connect_to_database()
        query = "INSERT INTO comic_books.scanned_upc_codes(upc_code, date_uploaded) VALUES (%s, %s);"
        time_now = datetime.datetime.now()
        date = str(time_now.year) + '-' + str(time_now.month) + '-' + str(time_now.day)
        for upc in self.scanned_barcodes_list:
            db.execute_query(self.db_cursor, query, (upc, date))

        self.db_cursor.close()

    def __print_list_barcodes(self):
        """ Prints a formatted list of barcodes with line numbers """
        line_no = 1

        for barcode in self.scanned_barcodes_list:
            print(f"\n({str(line_no) + ')':<7}{barcode}")
            line_no += 1

    def __delete_barcode_from_buffer_list(self):
        """
        Displays a list of barcodes scans and asks the user if there are any
        they would like to delete. If there are line items to delete, function
        removes barcodes and return new list.
        :return: List of barcodes after deleting any
        """
        num_barcodes = len(self.scanned_barcodes_list)

        self.__print_list_barcodes()

        delete_indexes = self.__get_lines_to_delete()

        # if there is anything to delete
        if delete_indexes:
            # confirm again they want to delete the following line items
            if input(
                    f"\nDelete these barcodes (y/n) "
                    f"{[self.scanned_barcodes_list[x] for x in delete_indexes]}?: "
            ).upper() == 'Y':

                list_after_delete = []
                delete_indexes = set(delete_indexes)

                for i in range(num_barcodes):
                    if i not in delete_indexes:
                        list_after_delete.append(self.scanned_barcodes_list[i])

                if list_after_delete:
                    return [x for x in list_after_delete]

                # deleted everything
                else:
                    return []
            # Try again
            else:
                return self.__delete_barcode_from_buffer_list()

        # nothing to delete
        return self.scanned_barcodes_list

    def __get_lines_to_delete(self) -> List[int]:
        """
        Gets the list of indexes user wants to delete. Return list of integer
        indexes or empty list if none
        :return:
        """
        num_barcodes = len(self.scanned_barcodes_list)
        lines = set(x for x in range(1, num_barcodes + 1))

        while True:
            # Ask the user which line(s) they want to delete
            which_line = input(
                "\nWhich line number (or space separated list "
                "of line numbers) would you like to delete "
                "(q to cancel)? : "
            ).strip()

            if which_line.upper() == 'Q':
                print("\nOk...not deleting any lines")
                return []

            else:
                # convert the input line numbers to a list
                which_line = which_line.split()
                valid_lines = True
                # verify the line numbers in the list are valid
                for line_no in which_line:
                    if int(line_no) not in lines:
                        print(f"\n{line_no} invalid line number...")
                        valid_lines = False

                if valid_lines is True:
                    if not which_line:
                        return []
                    else:
                        return [int(x) - 1 for x in which_line]


if __name__ == '__main__':
    my_scanner = Scanner()
    my_scanner.scan_barcodes_marvel()
    my_scanner.review_barcodes()
    print(my_scanner.scanned_barcodes_list)
