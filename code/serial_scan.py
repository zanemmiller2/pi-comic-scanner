"""
Author: Zane Miller
Adapted From: https://github.com/sparkfun/DE2120_Py/blob/main/examples/de2120_ex1_serial_scan.py
Email: millerzanem@gmail.com
Date: 04/13/2023
Description:
"""

from __future__ import print_function
import de2120_barcode_scanner
import serial
import sys
import time
from typing import *


def scanner_driver():
    """
    Example program to scan and print barcode
    :return:
    """
    serial_port = serial.Serial("/dev/cu.usbmodem141101", 115200, timeout=1)
    serial_scanner = de2120_barcode_scanner.DE2120BarcodeScanner(serial_port)

    if not serial_scanner.begin():
        print(
            "\nThe Barcode Scanner module isn't connected correctly to the system. Please check wiring",
            file=sys.stderr
        )
        return

    scanned_barcodes = read_barcodes(serial_scanner)


def read_barcodes(serial_scanner: de2120_barcode_scanner.DE2120BarcodeScanner) -> List[str]:
    """
    Reads barcodes from serial_scanner and returns them as a list
    :param serial_scanner: scanner object
    :return: list of scanned barcodes
    """

    barcode_list = []
    print("Scanner ready! Begin scanning...")
    while True:
        barcode_buffer = serial_scanner.read_barcode()
        # check if barcode was read
        if barcode_buffer:
            print(barcode_buffer)
            print("\nCode found: " + str(barcode_buffer))
            barcode_list.append(str(barcode_buffer))

            user_res = input("Would you like to scan more? (Y/N): ").lower()
            if user_res == 'n':
                break

            print("\nScan!")

        barcode_buffer = ""  # clear the buffer
        time.sleep(0.02)

    # return list of barcodes scanned
    print("\nDone scanning!")
    return barcode_list


if __name__ == '__main__':
    try:
        scanner_driver()
    except(KeyboardInterrupt, SystemExit) as exErr:
        print("\nEnding Example 1")
        sys.exit(0)
