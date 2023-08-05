# coding: utf-8
#!/usr/bin/env python
#
# Copyright 2014-2015 PredicSis

'''
PredicSis REST API Python bindings.
API docs at https://developer.predicsis.com/doc/
Authors: Michal Szczerbak <michal.szczerbak@predicsis.com>
'''

__author__='mszczerbak'
__version__ ='0.1'

import datetime

api_token = None
api_url = 'https://api.predicsis.com/'
tmp_storage = '.'
lvl_debug = 0

from predicsis.resource import Job, Project, Dataset, Dictionary, Target, Model, Scoreset, Report

def log(msg, level):
    if level <= lvl_debug:
        msg_final = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + '\t'
        if level == 1:
            msg_final += 'INFO'
        elif level == 2:
            msg_final += 'DEBUG'
        elif level == 3:
            msg_final += 'TRACE'
        elif level == -1:
            msg_final += 'ERROR'
        elif level == 0:
            msg_final += 'WARN'
        msg_final += '\t' + msg
        print msg_final