"""
Author: Zane Miller
Adapted From: https://github.com/sparkfun/DE2120_Py/blob/main/examples/de2120_ex1_serial_scan.py
Email: millerzanem@gmail.com
Date: 04/13/2023
Description: Class drivers for scanning by different methods
"""

from __future__ import print_function

import datetime
import time

import de2120_barcode_scanner
import serial


class InvalidConnectionException(Exception):
    """Raised the program cant connect to the serial port"""
    pass


BARCODE_CODE = "MAV18"
KEYBOARD_ENTRY_MODE = 'KYBD'
SCANNER_ENTRY_MODE = 'SCNR'
IDLE_SCANNER_TIMEOUT = 10
MAV18_LENGTH = 17
MAV18_LENGTH_SCANNED = 18


class Scanner:
    """
    Parent Scanner class inherited by MarvelBarcodeScanner and KeyboardBarcodeEntry subclasses.
    Handles most of the middleware between entry modes and review for upload to db.
    """

    def __init__(self, scanner_db):
        self.scanned_barcodes_list = []
        self.entry_mode = None
        self.db = scanner_db

    def enter_marvel_barcodes(self):
        """
        Generic function definition
        """
        pass

    ####################################################################################################################
    #
    #                                           REVIEW
    #
    ####################################################################################################################

    def review_barcodes(self):
        """
        Reviews the latest entry and asks the user if they want to make any modifications.
        """

        if self.get_num_barcodes() == 0:
            print("Nothing to review...\n")
            return

        self._print_list_barcodes()
        num_barcodes = self.get_num_barcodes()
        lines = {x + 1 for x in range(num_barcodes)}
        edit_response = self._get_edit_response(lines)

        # DO YOU WANT TO MAKE ANY CHANGES
        while str(edit_response).upper() != "N" and num_barcodes > 0:
            edit_index = int(edit_response)
            edit_index -= 1
            edit_barcode = self.scanned_barcodes_list[edit_index]
            edit_result = False

            while edit_result is False:
                print(f'(D)elete, (E)dit, or (C)ancel ({edit_barcode}): ')
                edit_action_response = input()

                # DELETE
                if edit_action_response.upper() == "D":
                    edit_result = self._delete_entry(edit_barcode, edit_index)

                # MODIFY ENTRY
                elif edit_action_response.upper() == "E":
                    edit_result = self._edit_entry(edit_barcode, edit_index)

                # CANCEL SELECTION
                elif edit_action_response.upper() == "C":
                    edit_result = True

                else:
                    print("Invalid Entry: Try Again...\n")
                    edit_result = False

            self._print_list_barcodes()
            num_barcodes = self.get_num_barcodes()
            lines = {x + 1 for x in range(num_barcodes)}
            edit_response = self._get_edit_response(lines)

    def _delete_entry(self, barcode: str, del_index: int) -> bool:
        print(f"Are you sure you want to delete {barcode} (y/n) ")
        delete_confirm = input()

        if delete_confirm.upper() == "Y":
            del self.scanned_barcodes_list[del_index]
            print(f"Deleted {barcode}\n")
            return True

        return False

    def _edit_entry(self, barcode: str, edit_index: int) -> bool:
        print(f"Are you sure you want to edit {barcode} (y/n) ")
        edit_confirm = input()

        if edit_confirm.upper() == 'Y':
            edited_barcode = input("Enter the updated barcode:\n")
            if len(edited_barcode) == MAV18_LENGTH:
                self.scanned_barcodes_list[edit_index] = str(edited_barcode)
                return True
            else:
                print(
                    f"MAV18 Barcode {edited_barcode} of length"
                    f" {len(edited_barcode)} is invalid (needs to be 17 digits)"
                )
                return False

        return False

    def _get_edit_response(self, lines) -> str:
        """
        Asks the user which line item they want to edit.
        :return: string response from user if line item is N or line is valid integer line number
        """
        res = input(
            "Which line would you like to edit? "
            "(enter a line number or (N) to save and continue): "
        )

        if res == 'N' or res == 'n':
            return 'N'

        if res.isnumeric():
            if int(res) in lines:
                return res
            else:
                print("Invalid line number...out of range")

        return self._get_edit_response(lines)

    ####################################################################################################################
    #
    #                                         DATABASE INTERACTIONS
    #
    ####################################################################################################################

    def upload_db(self):
        """
        asks the user if they wish to continue with uploading scanned upcs to backendDatabase buffer
        :return: true if upcs uploaded, false otherwise
        """
        # ask the user if they want to upload the list of _barcodes to the backendDatabase
        self._print_list_barcodes()
        upload_confirm = input(
            "These are the barcodes you scanned. Would you like the upload these barcodes (y/n)? "
        ).strip()

        if upload_confirm == 'N' or upload_confirm == 'n':
            return False
        elif upload_confirm == 'Y' or upload_confirm == 'y':
            self._upload_upcs_to_db()
            return True

    def _upload_upcs_to_db(self):
        """
        Uploads the list of scanned _barcodes to scanned_upc_codes buffer table in comic_books db,
        commits to db.
        :return: returns True if the upcs were uploaded to the db, false otherwise.
        """

        print("Uploading to db...")

        formatted_date = self.get_formatted_YYYY_MM_DD_string()

        # uploads each upc backend to db
        for upc in self.scanned_barcodes_list:
            query_params = (upc, formatted_date)
            self.db.upload_upc_to_buffer(query_params)

    ####################################################################################################################
    #
    #                                       GETTERS AND SETTERS
    #
    ####################################################################################################################

    def get_num_barcodes(self) -> int:
        """
        Counts the number of upc codes in scanned_barcodes_list buffer
        :return: an integer representing the number of upcs in list
        """
        return len(self.scanned_barcodes_list)

    def get_entry_method(self):
        """
        Returns the current entry_mode (scanner, keyboard) for inputting barcodes.
        """
        return self.entry_mode

    ####################################################################################################################
    #
    #                                       PARENT UTILITIES
    #
    ####################################################################################################################

    def _print_list_barcodes(self):
        """ Prints a formatted list of _barcodes with line numbers """
        line_no = 1

        for barcode in self.scanned_barcodes_list:
            print(f"({str(line_no) + ')':<5}{barcode}")
            line_no += 1

    @staticmethod
    def get_formatted_YYYY_MM_DD_string() -> str:
        """
        Returns the current time as a string in YYYY-MM-DD format
        :return: current time as string "YYYY-MM-DD"
        """
        # get current time in YYYY-MM-DD format
        time_now = datetime.datetime.now()
        return str(time_now.year) + '-' + str(time_now.month) + '-' + str(time_now.day)

    @staticmethod
    def format_marvel_barcode(mav18_barcode: str) -> str:
        """
        Appends the MAV18- backend to a mav18_barcode
        :param mav18_barcode:
        :return: formatted mav18_barcode as string with appended prefix
        """
        return "MAV18-" + mav18_barcode


class ScannerBarcodeEntry(Scanner):
    """
    Scanner object to handle connecting to scanner serial port,
    scanning _barcodes, and saving scanned _barcodes to file
    """

    def __init__(self, scanner_db, device_driver: str, baud_rate: int = 115200, timeout: int = 1):
        """
        Scanner object with hard_port, connection_status, DE2120BarcodeScanner
        serial_scanner object, and a list of scanned _barcodes
        """
        super().__init__(scanner_db)
        self.entry_mode = SCANNER_ENTRY_MODE
        self.device_driver = device_driver
        self.baud_rate = baud_rate
        self.timeout = timeout

        self._serial_port = serial.Serial("/dev/cu.usbmodem141101", 115200, timeout=1)
        self.serial_scanner = de2120_barcode_scanner.DE2120BarcodeScanner(self._serial_port)
        self._scanner_connection_status = False

        # try to connect to serial port
        try:
            self._connect_scanner()
        except InvalidConnectionException:
            exit(-1)

    def _connect_scanner(self):
        """
        Creates a connection to the supplied serial port and saves the status
        as self._connection_status.
        """
        self._scanner_connection_status = self.serial_scanner.begin()

        if not self._scanner_connection_status:
            raise InvalidConnectionException

        print("Scanner ready! Begin scanning...")

    def enter_marvel_barcodes(self):
        """
        Reads marvel _barcodes (UPC-A with a 5-digit add_on backend) from
        serial_scanner with a 5 digit add on backend. The first 3 digits of the
        add-on backend represent the issue number, the 4th digit represents the
        cover variant and the 5th digit represents the print variant.
        """

        if self._scanner_connection_status:
            user_continue_res = ""

            while user_continue_res.upper() != 'Q':

                print("Enter barcode with 5-digit add-on: ")
                marvel_barcode = False
                idle_time = time.time()

                # continue scanning or wait
                while marvel_barcode is False and user_continue_res.upper() != "Q":
                    # clear buffer before trying to read again
                    marvel_barcode = self.serial_scanner.read_barcode()

                    if not marvel_barcode and time.time() - idle_time >= IDLE_SCANNER_TIMEOUT:
                        user_continue_res = input(
                            "IDLE...What would you like to do?"
                            "\n\t(s) to continue scanning"
                            "\n\t(q) to save and continue:\n"
                        )

                        if user_continue_res.upper() == 'S':
                            break

                # check if a barcode was scanned
                if marvel_barcode:
                    marvel_barcode_length = len(str(marvel_barcode))

                    # check if the scanned barcode includes the 5 digit add on
                    # scanned barcode has an extra byte appended to the end
                    if marvel_barcode_length == MAV18_LENGTH_SCANNED:
                        formatted_marvel_barcode = self.format_marvel_barcode(str(marvel_barcode[:MAV18_LENGTH]))
                        if formatted_marvel_barcode not in self.scanned_barcodes_list:
                            print(f"Scanned {formatted_marvel_barcode}")
                            self.scanned_barcodes_list.append(formatted_marvel_barcode)
                        else:
                            print(f"{formatted_marvel_barcode} already scanned.")

                    # otherwise prompt to try again
                    else:
                        print(
                            f"Barcode {marvel_barcode[:marvel_barcode_length - 1]} of length {marvel_barcode_length} is invalid (needs to be 18 digits)"
                        )

                time.sleep(0.02)

        else:
            raise InvalidConnectionException


class KeyboardBarcodeEntry(Scanner):
    """Keyboard entry mode that inherits from Scanner parent class"""

    def __init__(self, scanner_db):

        super().__init__(scanner_db)
        self.entry_mode = KEYBOARD_ENTRY_MODE

    def enter_marvel_barcodes(self):
        """
        Reads marvel _barcodes (UPC-A with a 5-digit add_on backend) from
        user keyboard input with a 5 digit add on backend. The first 3 digits of the
        add-on backend represent the issue number, the 4th digit represents the
        cover variant and the 5th digit represents the print variant.
        """

        marvel_barcode = ""
        while marvel_barcode.upper() != "Q":
            marvel_barcode = input("Enter barcode with 5-digit add-on or (q) to quit: ")

            if marvel_barcode == 'q' or marvel_barcode == 'Q':
                break

            if len(marvel_barcode) == MAV18_LENGTH:
                formatted_marvel_barcode = self.format_marvel_barcode(marvel_barcode)
                if formatted_marvel_barcode not in self.scanned_barcodes_list:
                    print(f"\nScanned {formatted_marvel_barcode}")
                    self.scanned_barcodes_list.append(formatted_marvel_barcode)
                else:
                    print(f"{formatted_marvel_barcode} already scanned.")
            else:
                print(
                    f"MAV18 Barcode {marvel_barcode} of length "
                    f"{len(marvel_barcode)} is invalid (needs to be 17 digits)"
                )
