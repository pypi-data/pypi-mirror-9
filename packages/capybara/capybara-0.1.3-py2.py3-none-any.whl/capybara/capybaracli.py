#!/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import argparse

from amazon_wrapper import AmazonWrapper
from rakuten_wrapper import RakutenWrapper

aw = AmazonWrapper()
rw = RakutenWrapper()

def get(service, item=None):
    if service == 'rakuten':
        return rw.access_wrapper({'item_id': '%s' % item})
    elif service == 'amazon':
        return aw.access_wrapper({'asin': '%s' % item})
    else:
        return None

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Lemur: Wrapper for multiple tokens of multiple APIs')
    parser.add_argument('service', choices=['amazon', 'rakuten'], help="Service name")
    parser.add_argument('item', help="Item id")

    args = parser.parse_args()

    service = args.service
    item = args.item

    print get(service, item)



