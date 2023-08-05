#!/usr/bin/env python3

import configurator.formats._safe_importer
import os
import json

default_indent = 2

def load(filename):
    if os.path.exists(filename):
        with open(filename, mode='r') as f:
            return json.load(f)

def dump(filename, config, indent=default_indent):
    with open(filename, mode='w') as f:
        json.dump(config, f, indent=indent)
