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
        result = {}
        if option is not None:
            try:
                item_id = option['item']

                if 'type' in option and option['type'] == "genre":
                    payload = {
                        "format": "json",
                        "genreId": item_id,
                        "applicationId": token['applicationId']
                    }
                    r = requests.get(API_GENRE_BASE, params=payload)
                    data = r.json()
                    if not data['parents']:
                        result['genre'] = data['current']['genreName']
                    else:
                        result['genre'] = data['parents'][0]['parent']['genreName']
                elif 'type' not in option:
                    payload = {
                            "format": "json",
                            "itemCode": item_id,
                            "applicationId": token['applicationId']
                            }
                    r = requests.get(API_ITEM_BASE, params=payload)
                    data = r.json()
                    item = data['Items'][0]['Item']
                    result['raw'] = item
                    result['title'] = item['itemName']
                    result['url'] = item['itemUrl']
                    result['category_id'] = item['genreId']
                    opt = {"item": result["category_id"], "type": "genre"}
                    result['category'] = self.access_wrapper(opt)['genre']
                else:
                    result = None

            except:
                # If any exceptions happen, return None
                sys.stderr.write("Unexpected error accessing API:\n\t%s\n\t%s" % (sys.exc_info()[0], sys.exc_info()[1]))
                result = None

        return result


# class RakutenAPIObject(APIObject):
#     def __init__(self, api_type, raw):
#         APIObject.__init__(self)
#
#     def handle_raw_value(self, api_type, raw):
#         APIObject.handle_raw_value(self, raw)
#         if api_type == 'item':
#             self.raw = raw['Items'][0]['Item']
#             self.title = self.raw['itemName']
#             self.url = self.raw['itemUrl']
#             self.genre_id = self.raw['genreId']
#             # detail['category'] = get_genre(item['genreId'])
#         elif api_type == 'genre':
#             if raw['parents'] == []:
#                 self.genre = raw['current']['genreName']
#             else:
#                 self.genre = raw['parents'][0]['parent']['genreName']
#         else:
#             pass

