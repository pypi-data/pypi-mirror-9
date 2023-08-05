#!/usr/bin/env python3

import configurator.formats._safe_importer
import os
import imp

def load(filename):
    if os.path.exists(filename):
        module = imp.load_source('virtual', filename)
        config = {
            i: getattr(module, i)
            for i in dir(module)
            if not i.startswith('__') and not i.endswith('__')
        }
        return config

def dump(filename, config): # beta ~> without recursion ;)
    with open(filename, mode='w') as f:
        f.write('#!/usr/bin/env python3\n\n')
        for key, value in config.items():
            f.write('{} = \'{}\'\n'.format(key, value))
