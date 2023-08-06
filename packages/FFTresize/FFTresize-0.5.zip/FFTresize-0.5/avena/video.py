#!/usr/bin/env python

'''Read and write image and video files with OpenCV'''


from cv2 import cv
from numpy import asarray
from os.path import exists as _exists

from . import np
from . import utils


# Map of OpenCV image depths to NumPy array types
_cv_depths = {
    cv.IPL_DEPTH_8U:    'uint8',
    cv.IPL_DEPTH_8S:    'int8',
    cv.IPL_DEPTH_16U:   'uint16',
    cv.IPL_DEPTH_16S:   'int16',
    cv.IPL_DEPTH_32S:   'int32',
    cv.IPL_DEPTH_32F:   'float32',
    cv.IPL_DEPTH_64F:   'float64',
}


# Inverse mapping of the above
_cv_depths_inv = utils._invert_dict(_cv_depths)


# Map of colours to array indices
_OCV_RGB = {
    'B': 0,
    'G': 1,
    'R': 2,
}


def _template_image(image, depth):
    '''Return an empty image object of the same dimensions,
    colour depth, and number of channels as the given image.
    '''
    size = (image.width, image.height)
    channels = image.nChannels
    dup = cv.CreateImage(size, depth, channels)
    return dup


def _save_image(image, filename, random=False, ext=None):
    '''Save an image object and return the file name.

    If the parameter 'random' is True, use a random file name.
    '''
    if random:
        newfile = utils.rand_filename(filename, ext=ext)
    else:
        newfile = filename
    newimage = _template_image(image, cv.IPL_DEPTH_8U)
    cv.ConvertScaleAbs(image, newimage, scale=255)
    cv.SaveImage(newfile, newimage)
    return newfile


def num_frames(video_file):
    '''Return the number of frames in a video file.
    '''
    cap = cv.CaptureFromFile(video_file)
    if not cap:
        raise IOError('CaptureFromFile')
    n = cv.GetCaptureProperty(cap, cv.CV_CAP_PROP_FRAME_COUNT)
    return int(n)


def _cv_to_array(im, dtype=None):
    '''Return an OpenCV image object as a NumPy array.

    If a dtype is specified, return an array of that type.
    '''
    arr_data = im[:, :]
    arr_shape = (im.height, im.width, im.nChannels)
    if dtype is None:
        arr_dtype = np._np_dtypes[_cv_depths[im.depth]]
    else:
        arr_dtype = np._np_dtypes[dtype]
    arr = asarray(arr_data, dtype=arr_dtype)
    arr.shape = arr_shape
    return arr


def _array_to_cv(arr):
    '''Return a NumPy array as an OpenCV image object.
    '''
    utils.swap_rgb(arr, utils._PREFERRED_RGB, to=_OCV_RGB)
    im_channels = utils.depth(arr)
    swap = lambda x, y, z=1: (y, x)
    im_shape = swap(*arr.shape)
    im_size = arr.dtype.itemsize * im_channels * im_shape[0]
    im_depth = _cv_depths_inv[str(arr.dtype)]
    im = cv.CreateImageHeader(im_shape, im_depth, im_channels)
    cv.SetData(im, arr.tostring(), im_size)
    return im


DEFAULT_FRAME_ARRAY_DTYPE = 'float32'


_CV_CAM_PROPERTIES = {
    'width':    cv.CV_CAP_PROP_FRAME_WIDTH,
    'height':   cv.CV_CAP_PROP_FRAME_HEIGHT,
    'fps':      cv.CV_CAP_PROP_FPS,
}

DEFAULT_CAM_PROPERTY_RES = (640, 480)
DEFAULT_CAM_PROPERTY_FPS = 15


def _set_cam_properties(cap, props):
    for p in props:
        cv.SetCaptureProperty(
            cap,
            _CV_CAM_PROPERTIES[p],
            props[p]
        )


def get_frames(video_file=None,
               cam=-1, cam_res=None, cam_fps=None,
               as_array=True, dtype=None):
    '''Return a list of individual frames in a video file or
    webcam stream.

    If the parameter 'video_file' is None, frames are read
    from the default webcam.

    The optional parameter 'cam_res' specifies the webcam
    resolution as a (width, height) tuple in pixels, the
    default is (640, 480).

    The optional parameter 'cam_fps' specifies the webcam
    framerate in frames per second, the default is 15.

    If the parameter 'as_array' is True, return NumPy arrays.
    If dtype is specified, return NumPy arrays of that type.
    '''

    if dtype is None:
        dtype = DEFAULT_FRAME_ARRAY_DTYPE

    if cam_res is None:
        res = DEFAULT_CAM_PROPERTY_RES
    else:
        res = cam_res

    if cam_fps is None:
        fps = DEFAULT_CAM_PROPERTY_FPS
    else:
        fps = cam_fps

    if video_file:
        if not _exists(video_file):
            raise IOError(video_file)
        cap = cv.CaptureFromFile(video_file)
        if not cap:
            raise IOError('CaptureFromFile')
    else:
        cap = cv.CaptureFromCAM(cam)
        if not cap:
            raise IOError('CaptureFromCAM')
        cam_properties = {
            'width':    res[0],
            'height':   res[1],
            'fps':      fps,
        }
        _set_cam_properties(cap, cam_properties)

    while True:
        img = cv.QueryFrame(cap)
        if not img:
            break
        if as_array:
            img = _cv_to_array(img, dtype=dtype)
            np.normalize(img)
            utils.swap_rgb(img, _OCV_RGB, to=utils._PREFERRED_RGB)
        yield img


def _get_video_properties(filename):
    cap = cv.CaptureFromFile(filename)
    if not cap:
        raise IOError('CaptureFromFile')
    fps = cv.GetCaptureProperty(cap, cv.CV_CAP_PROP_FPS)
    width = cv.GetCaptureProperty(cap, cv.CV_CAP_PROP_FRAME_WIDTH)
    height = cv.GetCaptureProperty(cap, cv.CV_CAP_PROP_FRAME_HEIGHT)
    fps = float(fps)
    fps = min(fps, 30.0)
    fps = max(fps, 15.0)
    width = int(width)
    height = int(height)
    return (fps, width, height)


if __name__ == '__main__':
    pass
