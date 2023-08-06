#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  hzsunshx
# Created: 2015-02-06 14:23

"""

"""

import os
import sys
from PIL import Image
import cv2
import numpy as np

def image_change(src_filename, dst_filename, angle=90, text='fps: ?\nhello', color=(255, 255, 255)):
    pil_image = Image.open(src_filename)
    pil_image = pil_image.rotate(angle) # rotate
    cv2_image = np.array(pil_image.convert('RGB'))[:, :, ::-1].copy() # PIL to opencv

    h, w = cv2_image.shape[:2]

    font = cv2.FONT_HERSHEY_SIMPLEX
    nw, nh = w/6, h/4
    black_canvas = np.zeros((h, w, 3), dtype=np.uint8)
    base_height = h/20
    for line in text.split('\n'):
        cv2.putText(black_canvas, line, (w/20, base_height+20), font, 1.5, color, 4, 255)
        base_height += 50
    b2gray = cv2.cvtColor(black_canvas, cv2.COLOR_BGR2GRAY)
    ret, mask = cv2.threshold(b2gray, 2, 255, cv2.THRESH_BINARY)
    mask_inv = cv2.bitwise_not(mask)

    newimg = cv2.bitwise_or(cv2_image, black_canvas) #, mask=mask_inv)
    cv2.imwrite(dst_filename, newimg)

if __name__ == '__main__':
    #image_change(sys.argv[1], 'out.png', color=(255, 255, 255), text='filename: %s\n123455667\nabcdefg' % sys.argv[1])
    for filename in os.listdir('.'):
        if not filename.endswith('.png'):
            continue
        if filename.find('-') == -1:
            continue
        print '>>', filename
        idx, fps = filename[:-4].split('-')
        image_change(filename, 'out/%s.png' %(idx), text='FPS: %s' % fps)

