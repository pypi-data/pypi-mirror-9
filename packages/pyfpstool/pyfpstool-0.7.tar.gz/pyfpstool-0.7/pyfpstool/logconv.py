#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  hzsunshx
# Created: 2015-03-12 15:27

import os
import csv
import datetime
from . import rdlog

def __readfps(indir):
    data = rdlog.load_file(os.path.join(indir, 'fps.log'))
    nd = []
    for dt, value in data:
        timestamp = (dt - datetime.datetime(1970, 1, 1)).total_seconds()
        nd.append((timestamp, value['value']))
    return nd

def log2csv(indir, outdir):
    outfile = os.path.join(outdir, 'fps.csv')
    with open(outfile, 'wb') as csvfile:
        wr = csv.writer(csvfile)
        for timestamp, value in __readfps(indir):
            wr.writerow([timestamp, value])

def log2xls(indir, outdir):
    import xlwt
    outfile = os.path.join(outdir, 'fps.xls')
    excel_file = xlwt.Workbook()
    sheet = excel_file.add_sheet('Performance 1', cell_overwrite_ok=True)
    sheet.write(1, 2, 3)
    excel_file.save(outfile)
