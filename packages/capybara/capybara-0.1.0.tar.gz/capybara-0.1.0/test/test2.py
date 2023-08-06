#!/bin/python
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), '../lib/bin'))

from lemur import Lemur

l = Lemur(config_dir='../dsl/config/', tokens_dir='../dsl/tokens/')

c.get(service='rakuten', item='urutoragion:10000866')
c.get(service='amazon', item='B005CSYH5Y')
