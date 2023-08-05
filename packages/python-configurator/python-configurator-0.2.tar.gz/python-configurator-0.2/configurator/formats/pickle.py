#!/usr/bin/env python3

import configurator.formats._safe_importer
import os
import pickle

default_protocol = 0

def load(filename):
    if os.path.exists(filename):
        with open(filename, mode='rb') as f:
            return pickle.load(f)

def dump(filename, config, protocol=default_protocol):
    with open(filename, mode='wb') as f:
        pickle.dump(config, f, protocol)
