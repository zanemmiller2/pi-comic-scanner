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
import time
import sys


def run_example():
    """
    Example program to scan and print barcode
    :return:
    """
    serial_scanner = de2120_barcode_scanner.DE2120BarcodeScanner(serial.Serial("/dev/cu.usbmodem141101", 9600, timeout=1))

    if not serial_scanner.begin():
        print(
            "\nThe Barcode Scanner module isn't connected correctly to the system. Please check wiring",
            file=sys.stderr
        )
        return
    print("\nScanner ready!")

    scan_buffer = ""

    while True:
        scan_buffer = serial_scanner.read_barcode()
        if scan_buffer:
            print("\nCode found: " + str(scan_buffer))
            scan_buffer = ""

        time.sleep(0.02)


if __name__ == '__main__':
    try:
        run_example()
    except(KeyboardInterrupt, SystemExit) as exErr:
        print("\nEnding Example 1")
        sys.exit(0)
