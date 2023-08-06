#!/bin/python
# -*- coding: utf-8 -*-

from abst_wrapper import Wrapper

import os
import sys
import time
import datetime
import csv
import requests

SERVICE = 'rakuten'

API_ITEM_BASE="https://app.rakuten.co.jp/services/api/IchibaItem/Search/20140222"
API_GENRE_BASE="https://app.rakuten.co.jp/services/api/IchibaGenre/Search/20140222"

# Wrapper class for "Rakuten Item Search API(楽天商品検索API)"
class RakutenWrapper(Wrapper):
    def __init__(self):
        Wrapper.__init__(self, SERVICE)

    # Read and parse lib/tokens/rakuten_tokens.tsv
    def read_tokens(self, path):
        Wrapper.read_tokens(self, path)
        for row in self.tokens_reader:
            self.tokens.append({'applicationId': row[0].strip()})

    # Read and parse lib/config/rakuten_config.json
    def read_config(self, path):
        Wrapper.read_config(self, path)

    # Simple wrapper for single request for API request that returns a row response
    def single_access(self, token, option=None):
        Wrapper.single_access(self,token)
        try:
            item_id = option['item']
            payload = {
                    "format": "json",
                    "itemCode": item_id,
                    "applicationId": token['applicationId']
                    }
            r = requests.get(API_ITEM_BASE, params=payload)
            result = r.json()
        except:
            # If any exceptions happen, return None
            print "Unexpected error accessing API:\n\t" , sys.exc_info()[0], sys.exc_info()[1]
            result = None

        return result
