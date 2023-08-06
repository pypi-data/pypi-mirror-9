#!/usr/bin/env python

'''Read and write image files as NumPy arrays'''


from numpy import asarray, float32
from PIL import Image

from . import np
from . import utils


_DEFAULT_DTYPE = float32

_PIL_RGB = {
    'R': 0,
    'G': 1,
    'B': 2,
}


def get_channels(img):
    '''Return a list of channels of an image array.'''
    if utils.depth(img) == 1:
        yield img
    else:
        for i in range(utils.depth(img)):
            yield img[:, :, i]


def read(filename, dtype=_DEFAULT_DTYPE, normalize=True):
    '''Read an image file as an array.'''
    img = Image.open(filename)
    arr = asarray(img, dtype=dtype)
    utils.swap_rgb(arr, _PIL_RGB, to=utils._PREFERRED_RGB)
    if normalize:
        np.normalize(arr)
    return arr


def _pil_save(img, filename):
    pil_img = Image.fromarray(img)
    pil_img.save(filename)
    return


def save(img, filename, random=False, ext=None, normalize=False):
    '''Save an image array and return its path.'''
    if random:
        newfile = utils.rand_filename(filename, ext=ext)
    else:
        newfile = filename
    utils.swap_rgb(img, utils._PREFERRED_RGB, to=_PIL_RGB)
    if normalize:
        np.normalize(img)
    np.clip(img, np._dtype_bounds[str(img.dtype)])
    uint8img = np.to_uint8(img)
    _pil_save(uint8img, newfile)
    return newfile


if __name__ == '__main__':
    pass
