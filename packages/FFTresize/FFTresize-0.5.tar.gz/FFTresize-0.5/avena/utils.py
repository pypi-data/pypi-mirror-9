#!/usr/bin/env python

from os.path import exists, splitext
from random import randint


_depth = lambda x, y, z=1: z

_invert_dict = lambda d: dict((v, k) for k, v in list(d.items()))

_PREFERRED_RGB = {
    'R': 0,
    'G': 1,
    'B': 2,
}


def depth(array):
    '''Return the depth (the third dimension) of an array.'''
    return _depth(*array.shape)


def rand_filename(filename, ext=None):
    '''Return a unique file name based on the given file name.'''
    file_name, file_ext = splitext(filename)
    if ext is None:
        ext = file_ext
    while True:
        rand_file_name = file_name
        rand_file_name += '-'
        rand_file_name += str(randint(0, 10000))
        rand_file_name += ext
        if not exists(rand_file_name):
            break
    return rand_file_name


def swap_rgb(img, current, to):
    '''Swap the RBG channels of an image array.'''
    if depth(img) == 3 and not current == to:
        current_indices = list(map(current.get, ('R', 'G', 'B')))
        to_indices = list(map(to.get, ('R', 'G', 'B')))
        img[:, :, current_indices] = img[:, :, to_indices]


if __name__ == '__main__':
    pass
