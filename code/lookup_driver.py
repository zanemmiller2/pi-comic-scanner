"""
Author: Zane Miller
Email: millerzanem@gmail.com
Date: 04/16/2023
Description: Driver class for looking up scanned _barcodes
"""
import hashlib
import time

import requests

import keys.private_keys
import keys.pub_keys
from database import db_driver as db

COMICS_URL = "http://gateway.marvel.com/v1/public/comics"
CHARACTERS_URL = "http://gateway.marvel.com/v1/public/characters"
CREATORS_URL = "http://gateway.marvel.com/v1/public/creators"
EVENTS_URL = "http://gateway.marvel.com/v1/public/events"
SERIES_URL = "http://gateway.marvel.com/v1/public/series"
STORIES_URL = "http://gateway.marvel.com/v1/public/stories"


class Lookup:
    """ Lookup object responsible for looking up _barcodes in scanned upc buffer """

    def __init__(self, db_cursor):
        self._barcodes = {}
        self.comic_books = {}
        self._db_cursor = db_cursor

    ######################################################################
    #                       HTTPS INTERACTIONS
    ######################################################################
    def lookup_marvel_by_upc(self):
        """
        Sends the http request to /comics&upc= endpoint and store respose as comic_books object
        """
        hash_str, timestamp = self._get_marvel_api_hash()

        for barcode in self._barcodes:
            upc_code = barcode
            PARAMS = {
                'apikey': keys.pub_keys.marvel_developer_pub_key, 'ts': timestamp, 'hash': hash_str, 'upc': upc_code
            }
            request = requests.get(COMICS_URL, PARAMS)
            data = request.json()

            if data['data']['count'] == 0:
                print(f"No comics found with {upc_code} upc")

            # Store as a comic book object and add object to comic_books dictionary
            self.make_comic_book_object()

    ######################################################################
    #                 COMIC BOOK OBJECT INTERACTIONS
    ######################################################################

    def make_comic_book_object(self):
        """
        Store as a comic book object and add object to comic_books dictionary
        """
        pass

    ######################################################################
    #                       DATABASE INTERACTIONS
    ######################################################################
    def get_barcodes_from_db(self):
        """
        Queries the database for any _barcodes in the scanned_upc_codes table.
        """

        res_data = db.get_upcs_from_buffer(self._db_cursor)
        for upc in res_data:
            upc_prefix = upc['upc_code'][:5]
            upc_code = upc['upc_code'][6:]
            upload_date = upc['date_uploaded']

            if upc_prefix not in self._barcodes:
                self._barcodes[upc_prefix] = {}

            # new upc_code
            if upc_code not in self._barcodes[upc_prefix]:
                self._barcodes[upc_prefix][upc_code] = upload_date

            # Conflicting dates
            elif self._barcodes[upc_code][upc_code] != upload_date:
                self._barcodes[upc_code][upc_code] = self.reconcile_duplicate_upc(
                    self._barcodes[upc_code], upload_date
                )

            # duplicate with same date
            else:
                print("Duplicate barcode found but dates not conflicting...")

        print(self._barcodes)

    ######################################################################
    #                       GETTERS AND SETTERS
    ######################################################################
    def get_num_barcodes(self) -> int:
        """
        Gets the number of barcodes ready for api lookup
        :return: int length of self_barcodes{}
        """
        return len(self._barcodes)

    ######################################################################
    #                           UTILITIES
    ######################################################################
    @staticmethod
    def _get_marvel_api_hash():
        """
        Generates a md5 hash of timestamp + private key + public key
        :return: returns the hash digest and integer time stamp
        """

        timestamp = int(time.time())
        input_string = str(
            str(timestamp)
            + keys.private_keys.marvel_developer_priv_key
            + keys.pub_keys.marvel_developer_pub_key
        )

        return hashlib.md5(input_string.encode("utf-8")).hexdigest(), timestamp

    def reconcile_duplicate_upc(self, og_date, conflict_date):
        """
        Reconciles duplicate _barcodes with conflicting dates
        :param og_date: date from barcode previously scanned
        :param conflict_date: date of the current (newer) barcode
        :return: the user preferred date
        """

        print(
            f"Duplicate found with conflicting date. Which one do you want to keep:"
            f"\n\t(1) {og_date}"
            f"\n\t(2) {conflict_date}"
        )
        keep_res = input(">>> ")

        # keep the original date
        if keep_res[0] == '1':
            return og_date
        # keep the current date for barcode otherwise keep the original date for barcode
        elif keep_res[0] == '2':
            return conflict_date
        # invalid entry. try again
        else:
            print("Invalid entry...")
            return self.reconcile_duplicate_upc(og_date, conflict_date)


if __name__ == '__main__':
    lup = Lookup()

    # lup.lookup_by_upc("75960609724101711")
    lup.get_barcodes_from_db()
