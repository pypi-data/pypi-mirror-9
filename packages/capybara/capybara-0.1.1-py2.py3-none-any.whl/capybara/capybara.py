#!/bin/python
# -*- coding: utf-8 -*-

import os
from amazon_wrapper import AmazonWrapper
from rakuten_wrapper import RakutenWrapper

class Capybara:
    def __init__(self, config_dir=None, tokens_dir=None):
        self.wrappers = {}
        self.wrappers['amazon'] = AmazonWrapper()
        self.wrappers['rakuten'] = RakutenWrapper()

        for service, wrapper in self.wrappers.items():
            config_filename = './%s_config.json' % service
            tokens_filename = './%s_tokens.tsv' % service
            config_path = os.path.normpath(os.path.join(os.getcwd(), config_dir, config_filename))
            tokens_path = os.path.normpath(os.path.join(os.getcwd(), tokens_dir, tokens_filename))
            wrapper.setup(config_path, tokens_path)

    def get(self, service=None, item=None):
        return self.wrappers[service].access_wrapper({'item': item})

