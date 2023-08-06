#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  hzsunshx
# Created: 2015-03-09 16:16

__version__ = '0.3'

import signal
import time
import os
import sys
import hashlib
import subprocess
import platform
import click

from . import androaxml

__serialno = None
__dir__ = os.path.dirname(os.path.abspath(__file__))
__adb = 'adb'
__debug = False

def adb(cmd):
    if isinstance(cmd, list) or isinstance(cmd, tuple):
        cmd = subprocess.list2cmdline(__adb.split() + list(cmd))
    else:
        cmd = __adb + ' ' + cmd
    if __debug:
        print 'run', cmd
    ret = os.system(cmd)
    if ret != 0:
        raise RuntimeError('run command: %s, return %d' %(cmd, ret))
    return ret

@click.group()
@click.option('-s', '--serialno', default=None, help='Specify android device serial number if multi device connected')
@click.option('-d', '--debug', is_flag=True, help='Enable debug info')
def cli(serialno, debug):
    global __serialno, __adb, __debug
    __serialno = serialno
    __debug = debug
    if serialno:
        __adb = __adb + ' -s ' + __serialno

@cli.command(help='Check environment')
def doctor():
    paths = []
    for line in os.getenv('PATH').split(os.pathsep):
        if os.path.exists(os.path.join(line, 'adb' + ('.exe' if platform.system() == 'Windows' else ''))):
            paths.append(line)
    if len(paths) == 1:
        print 'Good'
    if len(paths) == 0:
        print 'No adb.exe found, download from: http://adbshell.com/download/'
    if len(paths) > 1:
        print 'adb found in %d paths, need to delete and keep one' % len(paths)
        for p in paths:
            print 'PATH:', p

def __start(package, logdir):
    selfdir = os.path.dirname(os.path.abspath(__file__))
    binfile = os.path.join(selfdir, 'byfpsmeter')
    m = hashlib.md5()
    m.update(open(binfile, 'r').read())
    md5sum = os.popen('adb shell md5 /data/local/tmp/byfpsmeter')
    if not md5sum.read().startswith(m.hexdigest()):
        print 'Install byfpsmeter'
        adb('push %s /data/local/tmp/' % binfile)
        adb('shell chmod 777 /data/local/tmp/byfpsmeter')
    args = []
    if package:
        args += ['-p', package]
    if logdir:
        args += ['-logdir', logdir]
    adb(['shell', '/data/local/tmp/byfpsmeter'] + args)

@cli.command(help='Start fps test')
@click.option('-p', '--package', help='Package name')
@click.option('-l', '--logdir', default='/data/local/tmp/_tmp', help='Out data generated dir in phone')
def start(package, logdir):
    __start(package, logdir)

def __convert(logdir, outdir):
    from . import draw
    adb(['pull', logdir, '_tmp'])
    draw.main(['-i', '_tmp', '-o', outdir])

@cli.command(help='Convert data to image file')
@click.option('-l', '--logdir', default='/data/local/tmp/_tmp', help='data generated dir in phone')
@click.option('-o', '--outdir', default='_out', help='Generated data dir')
def convert(logdir, outdir):
    __convert(logdir, outdir)

@cli.command(help='Start fps and convert after finish')
@click.option('-p', '--package', help='Package name')
@click.option('-l', '--logdir', default='/data/local/tmp/_tmp', help='data generated dir in phone')
@click.option('-o', '--outdir', default='_out', help='Generated data dir')
def run(package, logdir, outdir):
    try:
        __start(package, logdir)
    except:
        pass
    __convert(logdir, outdir)

@cli.command(help='Get package and activity name from apk')
@click.argument('apkfile', type=click.Path(exists=True))
def inspect(apkfile):
    pkg, act = androaxml.parse_apk(apkfile)
    click.echo('Package Name: "%s"' % pkg)
    click.echo('Activity: "%s"' % act)

def main():
    cli()

    #def handler(signum, frame):
    #    print 'Signal handler called with signal', signum
    #    os.system('adb shell killall byfpsmeter')
    #    sys.exit(0)
    #signal.signal(signal.SIGINT, handler)

    #cmdstr = subprocess.list2cmdline(['adb', 'shell', '/data/local/tmp/byfpsmeter']+sys.argv[1:])
    #os.system(cmdstr)
    #sys.exit(0)
    #while True:
    #    time.sleep(1.0)

if __name__ == '__main__':
    main()
