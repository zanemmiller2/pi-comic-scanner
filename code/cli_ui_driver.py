from serial_scan import *

SCANNER_INPUT_MODE = '1'
KEYBOARD_INPUT_MODE = '2'
QUIT_INPUT_MODE = '3'

if __name__ == '__main__':

    # ---------------------------------
    #       Scan or manual?
    # ---------------------------------
    input_method = None
    entry_cursor = None
    entry_method = None

    while input_method != SCANNER_INPUT_MODE and input_method != KEYBOARD_INPUT_MODE and input_method != QUIT_INPUT_MODE:
        input_method = input(
            "How would you like to upload barcodes?"
            "\n\t(1) Barcode Scanner"
            "\n\t(2) Keyboard Entry"
            "\n\t(3) Quit"
            "\n> "
        )

        # Scanner
        if input_method == SCANNER_INPUT_MODE:
            entry_cursor = ScannerBarcodeEntry(device_driver="/dev/cu.usbmodem141101")
            entry_method = "scanned"

        # Keyboard
        elif input_method == KEYBOARD_INPUT_MODE:
            entry_cursor = KeyboardBarcodeEntry()
            entry_method = "manually entered"

        # Quit
        elif input_method == QUIT_INPUT_MODE:
            print("Ok...Goodbye!")
            exit(1)

        # Invalid Input
        else:
            print("Invalid Entry")

    entry_cursor.enter_marvel_barcodes()

    # ---------------------------------
    #       Review
    # ---------------------------------
    review_res = ""
    while review_res.upper() != "N" and entry_cursor.get_num_barcodes() > 0:
        review_res = input("Would you like to review your entries (y/n)?: ")

        if review_res.upper() == "Y":
            entry_cursor.review_barcodes()
        elif review_res.upper() != "N":
            print("Invalid entry...\n")

    if entry_cursor.get_num_barcodes() == 0:
        print("Nothing left to review. Goodbye...")
        exit(1)

    # ---------------------------------
    #       Upload to DB
    # ---------------------------------
    db_upload_res = ""

    # Print the list of barcodes
    # Ask the user if they want to upload the barcodes to the database
    # If they do:
    # User enter database credentials via command line
    # Validate credentials
    # Confirm upload
    # Comit
    # If they do not:
    # Confirm
    # exit

    print(entry_cursor.scanned_barcodes_list)
