#!/usr/bin/env python3

import argparse
import importlib

class convertor():

    def __init__(self, source_filename, source_format='python', target_format='json', target_filename=False, debug=False):
        if not target_filename: target_filename = '{}.{}'.format(source_filename, target_format)
        self.source = importlib.import_module('configurator.formats.{}'.format(source_format))
        self.target = importlib.import_module('configurator.formats.{}'.format(target_format))
        config = self.source.load(source_filename)
        if debug: print(config)
        self.target.dump(target_filename, config)

if __name__ == '__main__':
    choices=['python', 'pickle', 'json']
    parser = argparse.ArgumentParser(description='Convert configuration file.')
    parser.add_argument('-s', '--source_format', help='source format', default='python', choices=choices)
    parser.add_argument('-t', '--target_format', help='target format', default='json', choices=choices)
    #group = parser.add_mutually_exclusive_group()
    #group.add_argument('-d', '--debug', action='store_true')
    #group.add_argument('-v', '--verbose', action='count')
    parser.add_argument('source_filename', help='source filename')
    parser.add_argument('target_filename', help='target filename')
    #parser.add_argument('source_filename', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
    #parser.add_argument('target_filename', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
    #parser.print_help()
    args = parser.parse_args()
    #args = parser.parse_args('-s python -t python'.split()) # source_format='python', target_format='python'
    #args = parser.parse_args('-d'.split()) # debug=True
    #args = parser.parse_args('-vvv'.split()) # verbose=3
    #if args.debug or args.verbose: print(args)
    convertor(args.source_filename, args.source_format, args.target_format, args.target_filename)
