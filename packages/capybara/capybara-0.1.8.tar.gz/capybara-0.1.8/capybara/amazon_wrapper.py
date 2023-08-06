#!/bin/python
# -*- coding: utf-8 -*-

from abst_wrapper import Wrapper

import os
import sys
import time
import datetime
import csv

from amazon.api import AmazonAPI

SERVICE = 'amazon'

# Wrapper class for "Amazon Product Advertising API"
class AmazonWrapper(Wrapper):
    def __init__(self):
        Wrapper.__init__(self, SERVICE)

    # Read and parse lib/tokens/amazon_tokens.tsv
    def read_tokens(self, path):
        Wrapper.read_tokens(self, path)
        for row in self.tokens_reader:
            self.tokens.append({'ACCESS_KEY': row[0].strip(), 'SECRET_KEY': row[1].strip(), 'ASSOC_TAG': row[2].strip(), 'LOCALE': row[3].strip()})

    # Read and parse lib/config/amazon_config.json
    def read_config(self, path):
        Wrapper.read_config(self, path)

    # Simple wrapper for single request for API request that returns a row response
    def single_access(self, token, option=None):
        Wrapper.single_access(self,token)
        result = {}
        try:
            asin = option['item']
            amazon = AmazonAPI(token['ACCESS_KEY'], token['SECRET_KEY'], token['ASSOC_TAG'], region=token['LOCALE'])
            data = amazon.lookup(ItemId=asin)
            result['raw'] = data
            result['title'] = data.title
            result['category'] = data.get_attribute('ProductGroup')

        except:
            # If any exceptions happen, return None
            sys.stderr.write("Unexpected error accessing API:\n\t%s\n\t%s" % (sys.exc_info()[0], sys.exc_info()[1]))
            result = None

        return result

