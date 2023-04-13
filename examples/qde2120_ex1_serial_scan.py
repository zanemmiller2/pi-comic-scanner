#!/usr/bin/env python
# -----------------------------------------------------------------------------
# qde2120_ex1_serial_scan.py
# ------------------------------------------------------------------------
#
# Written by Priyanka Makin @ SparkFun Electronics, April 2021
#
# This example demonstrates how to get the scanner connected and will output
# and barcode it sees.
#
#  
# Do you like this library? Help support SparkFun. Buy a board!
#
# ==================================================================================
# Copyright (c) 2021 SparkFun Electronics
#
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal 
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all 
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
# SOFTWARE.
# ==================================================================================
# Example 1

from __future__ import print_function
import de2120_barcode_scanner
import time
import sys


def run_example():
    """
    Example program to scan and print barcode
    :return:
    """
    print("\nSparkFun DE2120 Barcode Scanner Breakout Example 1")
    my_scanner = de2120_barcode_scanner.DE2120BarcodeScanner()

    if not my_scanner.begin():
        print(
            "\nThe Barcode Scanner module isn't connected correctly to the system. Please check wiring",
            file=sys.stderr
        )
        return
    print("\nScanner ready!")

    scan_buffer = ""

    while True:
        scan_buffer = my_scanner.read_barcode()
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
