#!/usr/bin/env python
''' monkeytime
Patch datetime for functions and increased performance of strptime
'''
import imp
import monkeydatetime

datetime = imp.load_module('datetime', *imp.find_module('datetime'))
datetime.datetime = monkeydatetime.datetime
