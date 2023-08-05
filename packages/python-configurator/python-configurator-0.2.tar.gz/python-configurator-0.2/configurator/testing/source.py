#!/usr/bin/env python3

key = 'default'
folder = '/home/pm/projects/foo/sqlite/'
connector = 'sqlite'
target = '/home/pm/projects/foo/foo.db'

if __name__ == '__main__':
    from configurator.convertor import convertor
    convertor(__file__, debug=True)
    convertor(__file__, 'python', 'pickle', debug=True)
    convertor(__file__, 'python', 'python', debug=True)
