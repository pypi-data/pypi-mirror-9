#!/usr/bin/env python3

import sys
import os

directory = os.path.dirname(os.path.abspath(__file__)) # the directory of the script being run
#print(directory)
#directory = os.getcwd() # the current working directory
#print(directory)

while sys.path.count(directory): sys.path.remove(directory) # remove directory from pythonpath
