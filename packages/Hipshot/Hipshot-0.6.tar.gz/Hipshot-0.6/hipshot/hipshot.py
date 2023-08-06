#!/usr/bin/env python2

'''Hipshot converts a video file or series of photographs into
a single image simulating a long-exposure photograph.
'''

import cv
from numpy import copy

from avena import image, np, video


__author__ = 'Mansour Moufid'
__copyright__ = 'Copyright 2013-2015, Mansour Moufid'
__license__ = 'ISC'
__version__ = '0.6'
__email__ = 'mansourmoufid@gmail.com'
__status__ = 'Development'


_EXT = '.png'


def merge(frames, alpha, display=None):
    '''Average a list of frames with a weight of alpha,
    optionally display the process in an OpenCV NamedWindow.
    '''
    first = frames.next()
    acc = first * alpha
    for frame in frames:
        acc += frame * alpha
        if display:
            display_acc = copy(acc)
            display_acc = video._array_to_cv(display_acc)
            cv.ShowImage(display, display_acc)
            k = cv.WaitKey(1)
            k = k & 255
            if k == ord('q'):
                break
            elif k == ord('z'):
                acc.fill(0)
    return acc


if __name__ == '__main__':
    pass
