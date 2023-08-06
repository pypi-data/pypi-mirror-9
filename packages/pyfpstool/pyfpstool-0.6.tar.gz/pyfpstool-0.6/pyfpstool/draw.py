#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  hzsunshx
# Created: 2015-02-06 17:28

"""
draw line -_/\
"""

import os
import sys
import argparse
import json
import time
import datetime

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.transforms import offset_copy
except:
    sys.exit('Need python-matplotlib installed, download from: http://matplotlib.org/downloads.html')


sysinfo = None

def process_log(filename, fn):
    ''' handle each log line by line '''
    if not os.path.exists(filename):
        print 'log(%s) not found' %(filename)
        return False

    for line in open(filename):
        if not line:
            continue
        v = json.loads(line)
        strtime, msec = v.get('time').split('.')
        curtime = time.strptime(strtime, '%Y-%m-%d %H:%M:%S')
        timestamp = time.mktime(curtime)
        timestamp += float('0.'+msec)
        dtime = datetime.datetime.fromtimestamp(timestamp)

        fn(dtime, v.get('value'))
    return True

def draw_chart(xres, data, textfmt='', title='chart', ylabel='y', outfile=None, format_time=True):
    '''
    @xres: list
    @data: list(list)
    @title: string
    '''
    plt.clf() # clear
    fig, ax = plt.subplots()
    transOffset = offset_copy(ax.transData, fig=fig, y = 6, units='dots')
    lines = []
    for dset in data:
        line = ax.plot(xres, dset, 'o-') # draw lines
        lines.append(line)
        last_value = [0] # plot value
        for i, dtime in enumerate(xres):
            value = dset[i]
            if last_value[0] != value:
                if textfmt:
                    plt.text(dtime, value, textfmt %(value), transform=transOffset) # draw value
                last_value[0] = value
    
    if format_time:
        fig.autofmt_xdate()
    plt.xlabel(title, fontsize=14, fontweight='bold')
    # plt.title(title)
    plt.ylabel(ylabel)
    plt.grid(True)
    if outfile:
        plt.savefig(outfile)
    return lines

def load_fps_data(input_dir, output_dir):
    xres = []
    yres = []
    def handle_data(dtime, v):
        xres.append(dtime)
        value = v.get('value')
        yres.append(value)

        index = v.get('index')
        if os.path.exists(os.path.join(input_dir, '%d.png' % index)):
            try:
                print index
                from . import rotate
                rotate.image_change(os.path.join(input_dir, str(index)+'.png'),
                        os.path.join(output_dir, '%s.png' %index),
                        text='FPS: %s\nTime: %s' % (value, dtime.strftime('%H:%M:%S')))
            except Exception, e:
                print index, e

    fps_logfile = os.path.join(input_dir, 'fps.log')
    fps_imgfile = os.path.join(output_dir, 'fps.png')
    fpscdf_imgfile = os.path.join(output_dir, 'fps-cdf.png')

    ok = process_log(fps_logfile, handle_data)
    if not ok:
        return
    draw_chart(xres, [yres], textfmt='', title='FPS Chart', ylabel='fps', outfile=fps_imgfile)
    # CDF
    cnt = {}
    for y in yres:
        cnt[y] = cnt.get(y, 0) + 1
    keys = sorted(cnt.keys())
    nxs, nys = [], []
    n = 0
    for v in keys:
        n += cnt[v]
        nys.append(float(n)/len(yres))
        nxs.append(v)
    draw_chart(nxs, [nys], title='CDF', outfile=fpscdf_imgfile, format_time=False)


def load_mem_data(input_dir, output_dir):
    logfile = os.path.join(input_dir, 'mem.log')
    imgfile = os.path.join(output_dir, 'mem.png')
    xres = []
    uss, pss, rss, vss = [], [], [], []
    def handle_data(dtime, v):
        xres.append(dtime)
        vval = round(v.get('vss')/1024.0, 2)
        rval = round(v.get('rss')/1024.0, 2)
        pval = round(v.get('pss')/1024.0, 2)

        vss.append(vval)
        rss.append(rval)
        pss.append(pval)
        uval = v.get('uss')
        if uval:
            uval = round(uval/1024.0, 2)
            uss.append(uval)

    ok = process_log(logfile, handle_data)
    if not ok:
        return
    data = [vss, pss, rss]
    ylabel = 'pss, rss, vss MB'
    if uss:
        data.append(uss)
        ylabel = 'uss, '+ ylabel
    draw_chart(xres, data, textfmt='%d', title='Memory Chart', ylabel=ylabel, outfile=imgfile)

def load_cpu_data(input_dir, output_dir):
    xres = []
    vals = []
    def handle_data(dtime, v):
        v = round(v, 2)
        xres.append(dtime)
        vals.append(v)

    logfile = os.path.join(input_dir, 'cpu.log')
    imgfile = os.path.join(output_dir, 'cpu.png')

    ok = process_log(logfile, handle_data)
    if not ok:
        return

    ncpu = sysinfo['num_cpu']
    title = 'CPU Chart (num cpu: %d)' %(ncpu)
    draw_chart(xres, [vals], title=title, ylabel='cpu [0~%d]%%'%(ncpu*100), textfmt='%.2f', outfile=imgfile)

def load_syscpu_data(input_dir, output_dir):
    ncpu = sysinfo['num_cpu']
    xres = []
    data = []
    avgs = []
    for i in range(ncpu):
        data.append([])
    
    def handle_data(dtime, v):
        xres.append(dtime)
        for i in range(ncpu):
            data[i].append(v['per'][i])
        avgs.append(v['all'])
    data.append(avgs)
    logfile = os.path.join(input_dir, 'syscpu.log')
    imgfile = os.path.join(output_dir, 'syscpu.png')
    ok = process_log(logfile, handle_data)
    if not ok:
        return

    title = 'System CPU Chart (num cpu: %d)' %(ncpu)
    lines = draw_chart(xres, data, title=title, ylabel='cpu [0~100]%', textfmt='')
    plt.setp(lines[0], linewidth=4)
    plt.setp(lines[0], markersize = 8)
    plt.legend(('Average', 'cpu1', 'cpu2', 'cpu3', 'cpu4'), loc = 'upper right')
    plt.savefig(imgfile)

def main(args=None):
    parser = argparse.ArgumentParser(description='Convert byfpsmeter generated files')
    parser.add_argument('-i', '--input', default='_tmp', type=str, help='input dir')
    parser.add_argument('-o', '--output', default='_out', type=str, help='output dir')
    args = parser.parse_args(args)
    if not os.path.isdir(args.input):
        sys.exit('Require input(%s) exists and is directory' % args.input)
    if not os.path.exists(args.output):
        os.makedirs(args.output)

    global sysinfo
    sysinfo = json.loads(open(os.path.join(args.input, 'sysinfo.log')).read())

    for fn in (load_fps_data, load_mem_data, load_cpu_data, load_syscpu_data):
        print fn.__name__
        fn(args.input, args.output)

if __name__ == '__main__':
    main()
