#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  hzsunshx
# Created: 2015-03-09 16:16

__version__ = '0.1'

import signal
import time
import os
import sys
import hashlib
import subprocess

def main():
    selfdir = os.path.dirname(os.path.abspath(__file__))
    binfile = os.path.join(selfdir, 'byfpsmeter')
    m = hashlib.md5()
    m.update(open(binfile, 'r').read())
    md5sum = os.popen('adb shell md5 /data/local/tmp/byfpsmeter')
    if not md5sum.read().startswith(m.hexdigest()):
        print 'Install byfpsmeter'
        os.system('adb push %s /data/local/tmp/' % binfile)
        os.system('adb shell chmod 777 /data/local/tmp/byfpsmeter')

    #def handler(signum, frame):
    #    print 'Signal handler called with signal', signum
    #    os.system('adb shell killall byfpsmeter')
    #    sys.exit(0)
    #signal.signal(signal.SIGINT, handler)

    cmdstr = subprocess.list2cmdline(['adb', 'shell', '/data/local/tmp/byfpsmeter']+sys.argv[1:])
    os.system(cmdstr)
    #sys.exit(0)
    #while True:
    #    time.sleep(1.0)

if __name__ == '__main__':
    main()
