#!/usr/bin/env python2

'''FFTresize resizes images using zero-padding in the frequency
domain.
'''

from avena import image, utils
from numpy import zeros as _zeros

from . import fftinterp


__author__ = 'Mansour Moufid'
__copyright__ = 'Copyright 2013-2015, Mansour Moufid'
__license__ = 'ISC'
__version__ = '0.5'
__email__ = 'mansourmoufid@gmail.com'
__status__ = 'Development'


_EXT = '.png'


def resize(filename, factor=1.5):
    '''Resize an image by zero-padding in the frequency domain.

    Return the filename of the resized image.
    '''
    img = image.read(filename)
    nchannels = utils.depth(img)
    if nchannels == 1:
        new = fftinterp.interp2(img, factor)
    else:
        new = None
        for i in range(nchannels):
            rgb = img[:, :, i]
            newrgb = fftinterp.interp2(rgb, factor)
            if new is None:
                newsize = list(newrgb.shape)
                newsize.append(nchannels)
                new = _zeros(tuple(newsize))
            new[:, :, i] = newrgb
    return image.save(new, filename, random=True, ext=_EXT, normalize=True)


if '__main__' in __name__:
    pass
