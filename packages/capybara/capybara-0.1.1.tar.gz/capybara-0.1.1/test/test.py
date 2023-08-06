#!/bin/python
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), '../bin'))

from amazon_wrapper import AmazonWrapper as AW
from rakuten_wrapper import RakutenWrapper as RW

aw = AW()
for i in range(3):
    print aw.access_wrapper()

rw = RW()
for i in range(3):
    print rw.access_wrapper()


