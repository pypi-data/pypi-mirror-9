#!/usr/bin/env python2

'''2D spatial filtering with the FFT'''


from numpy import empty as _empty, real as _real
from numpy.fft import irfft2 as _irfft2, rfft2 as _rfft2

from . import image, utils


def _zero_low_freq(array, rows, columns):
    m, n = array.shape[:2]
    p, q = rows, columns
    border_coord_pairs = [
        ((0, 0), (p, n)),       # Top edge
        ((m - p, 0), (m, n)),   # Bottom edge
        ((0, 0), (m, q)),       # Left edge
        ((0, n - q), (m, n)),   # Right edge
    ]
    for (a, b), (c, d) in border_coord_pairs:
        array[a:c, b:d] = 0.0


def highpass(array, rows, columns):
    '''Apply a 2D high-pass filter to an image array.'''
    z = _empty(array.shape, dtype=array.dtype)
    for i, c in enumerate(image.get_channels(array)):
        C = _rfft2(c)
        _zero_low_freq(C, rows, columns)
        c = _irfft2(C, s=c.shape)
        c = _real(c)
        if utils.depth(array) > 1:
            z[:, :, i] = c
        else:
            z = c
    return z


if __name__ == '__main__':
    pass
