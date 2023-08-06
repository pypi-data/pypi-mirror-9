#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  hzsunshx
# Created: 2015-03-12 15:24

"""
read log
"""

import os
import time
import datetime
import json

def load_file(filename):
    ''' handle each log line by line '''
    if not os.path.exists(filename):
        print 'log(%s) not found' %(filename)
        return None

    data = []
    for line in open(filename):
        if not line:
            continue
        v = json.loads(line)
        strtime, msec = v.get('time').split('.')
        curtime = time.strptime(strtime, '%Y-%m-%d %H:%M:%S')
        timestamp = time.mktime(curtime)
        timestamp += float('0.'+msec)
        dtime = datetime.datetime.fromtimestamp(timestamp)

        data.append((dtime, v.get('value')))
    return data

