#!/bin/python
# -*- coding: utf-8 -*-

# Base class from which each service's wrapper derives.

# Note:
#   method "read_tokens" will vary from one service to another service.
#   method "single_access" will vary from one service to another service.

# TODO: Enable reading tokens/config files outside lib directory
# TODO: Better exception handling

import os
import sys
import time
import datetime
import csv
import json

SLEEP_TIME=0.1 # TODO: Optimization of SLEEP_TIME
BIN_DIR = os.path.dirname(os.path.abspath(__file__))
# TOKENS_DIR = os.path.normpath(os.path.join(BIN_DIR,'../tokens/'))
DEFAULT_CONFIG_DIR = os.path.normpath(os.path.join(BIN_DIR,'../config/'))

class Wrapper:
    def __init__(self, service):
        self.last_request_time = datetime.datetime.now()
        self.service = service
        self.access_count = 0

    def setup(self, config_path, tokens_path):
        self.read_tokens(tokens_path)
        self.read_config(config_path)

    # Read lib/tokens/xxx_tokens.tsv
    def read_tokens(self, path):
        if path is None:
            sys.stderr.write('Using default config...')
            self.tokens_filename = './default_%s_tokens.tsv' % self.service
            self.tokens_path = os.path.normpath(os.path.join(TOKENS_DIR, self.tokens_filename))
        else:
            self.tokens_path = path

        try:
            self.tokens_reader = csv.reader(file(self.tokens_path), delimiter='\t')
        except:
            sys.stderr.write("Unexpected error while reading %s:\n\t%s\n\t%s" % (self.tokens_path , sys.exc_info()[0], sys.exc_info()[1]))

        self.tokens = []

    # Read lib/config/xxx_config.json
    def read_config(self, path):
        if path is None:
            sys.stderr.write('Using default config...')
            self.config_filename = './default_%s_config.json' % self.service
            self.config_path = os.path.normpath(os.path.join(DEFAULT_CONFIG_DIR, self.config_filename))
        else:
            self.config_path = path

        try:
            self.config_reader = open(self.config_path)
            self.config = json.load(self.config_reader)
        except:
            sys.stderr.write("Unexpected error while reading %s:\n\t%s\n\t%s" % (self.config_path , sys.exc_info()[0], sys.exc_info()[1]))
            self.config = {'interval': 1000, 'slow':1}
            sys.stderr.write('Using default config...')

    # Calculate actual interval and roop over tokens to wait and throw request
    def access_wrapper(self, option=None):
        # Calculate actual time interval based on config.
        interval = float(self.config['slow']) * float(self.config['interval']) / float(len(self.tokens))

        # Wait until request allowed
        now = datetime.datetime.now()
        print 'Waiting %s[ms] ...' % interval
        while now <= self.last_request_time + datetime.timedelta(milliseconds=int(interval)):
            time.sleep(SLEEP_TIME)
            now = datetime.datetime.now()

        index = self.access_count % len(self.tokens)
        token = self.tokens[index]
        result = self.single_access(token, option)
        return result

    # Simple wrapper for single request for each API request that returns a row response
    def single_access(self, token, option=None):
        self.access_count += 1
        return token
        
