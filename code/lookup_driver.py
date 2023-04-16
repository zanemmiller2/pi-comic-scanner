"""
Author: Zane Miller
Email: millerzanem@gmail.com
Date: 04/16/2023
Description: Driver class for looking up scanned barcodes
"""
import hashlib
import time

import requests

import keys.private_keys
import keys.pub_keys

COMICS_URL = "http://gateway.marvel.com/v1/public/comics"


class Lookup:
    """Lookup object responsible for looking up barcodes in scanned upc buffer """

    def __init__(self):
        self.barcodes = []
        self.comic_books = {}

    def _get_marvel_api_hash(self):
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

    def lookup_by_upc(self, upc_code):
        """
        Sends the http request to /comics&upc= endpoint.
        :param upc_code: 18 digit comic book upc code
        """
        hash_str, timestamp = self._get_marvel_api_hash

        PARAMS = {'apikey': keys.pub_keys.marvel_developer_pub_key, 'ts': timestamp, 'hash': hash_str, 'upc': upc_code}
        request = requests.get(COMICS_URL, PARAMS)

        print(request.json())

    def get_barcodes(self):
        pass


if __name__ == '__main__':
    lup = Lookup()

    lup.lookup_by_upc("75960609724101711")
