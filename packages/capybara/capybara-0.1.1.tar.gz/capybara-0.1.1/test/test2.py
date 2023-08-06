#!/bin/python
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), '../capybara'))

from capybara import Capybara

c = Capybara(config_dir='../local/config/', tokens_dir='../local/tokens/')

c.get(service='rakuten', item='urutoragion:10000866')
c.get(service='amazon', item='B005CSYH5Y')
