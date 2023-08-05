#!/usr/bin/env python
# coding: utf-8
"""
Audio Frames Toolkit
"""

# Python Standard Library
from __future__ import division
import doctest

# Third-Party Libraries
import numpy as np

#
# Metadata
# ------------------------------------------------------------------------------
#
__main__ = (__name__ == "__main__")

from audio.about_frames import *

#
# TODO
# ------------------------------------------------------------------------------
#
#   - support split/merge of multi-channel data.
#

#
# Application Programming Interface
# ------------------------------------------------------------------------------
#
def split(data, frame_length, pad=False, overlap=0, window=None):
    """
    Split an array into frames.

    Arguments
    ---------

      - `data`: a sequence of numbers,

      - `frame_length`: the desired frame length,

      - `pad`: if `True`, zeros are added to the last frame to make it
        match the prescribed frame length. If the length of the last frame
        differs from the prescribed length and pad is `False`, the function
        fails (this is the default behavior).

      - `overlap`: number of samples shared between successive frames,
        defaults to `0`.

      - `window`: an optional window applied to each frame after the split.
        The default (rectangular window) does not modify the frames.

    Result
    ------

      - `frames`: a sequence of numpy arrays.
    """
    data = np.array(data, copy=False)
    length = len(data)
    if overlap >= frame_length:
        error = "overlap >= frame_length"
        raise ValueError(error)
    frame_shift = frame_length - overlap
    num_frames, remain = divmod(length - overlap, frame_shift)
    extra = (frame_shift - remain) % frame_shift

    if extra:
        if pad is False:
            error = "cannot split the data into an entire number of frames."
            raise ValueError(error)
        else:
            data = np.r_[data, np.zeros(extra, dtype=data.dtype)]
            length = len(data)
            num_frames += 1

    if window is None:
        window = np.ones
    window_ = window(frame_length)

    frames = np.empty((num_frames, frame_length), dtype=data.dtype)

    for i in range(num_frames):
        start = i * frame_shift
        stop  = start + frame_length
        frames[i] = window_ * data[start:stop]

    return frames


def merge(frames, overlap=0, window=None):
    """
    Merge a sequence of frames of the same length.

    Arguments
    ---------

      - `frames`: a sequence of frames with the same length,

      - `overlap`: number of overlapping samples between successive frames,
        defaults to `0`.

      - `window`: an optional window applied to each frame before the merge.
        The default (rectangular window) does not modify the frames.

    Result
    ------

      - `data`: a numpy array.
"""
    frames = np.array(frames, copy=False)
    num_frames, frame_length = np.shape(frames)
    if overlap >= frame_length:
        error = "overlap >= frame_length"
        raise ValueError(error)
    frame_shift = frame_length - overlap
    if window is None:
        window = np.ones
    window_ = window(frame_length)

    data = np.zeros(frame_length + (num_frames - 1) * frame_shift, 
                    dtype=frames.dtype)
    
    for i in range(num_frames):
        start = i * frame_shift
        stop  = start + frame_length
        data[start:stop] += window_ * frames[i]

    return data

#
# Doctests
# ------------------------------------------------------------------------------
#

__doc__ += \
"""

Preamble
--------------------------------------------------------------------------------

    >>> import numpy as np

Test sequence
--------------------------------------------------------------------------------

    >>> data = [1, 2, 3, 4, 5, 6]

Basic Usage
--------------------------------------------------------------------------------

    >>> split(data, 1)
    array([[1],
           [2],
           [3],
           [4],
           [5],
           [6]])
    >>> split(data, 2)
    array([[1, 2],
           [3, 4],
           [5, 6]])
    >>> split(data, 3)
    array([[1, 2, 3],
           [4, 5, 6]])
    >>> split(data, 4) # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ValueError: ...
    >>> split(data, 5) # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ValueError: ...
    >>> split(data, 6)
    array([[1, 2, 3, 4, 5, 6]])
    >>> split(data, 7) # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ValueError: ...


Zero Padding Enabled
--------------------------------------------------------------------------------

    >>> split(data, 1, pad=True)
    array([[1],
           [2],
           [3],
           [4],
           [5],
           [6]])
    >>> split(data, 2, pad=True)
    array([[1, 2],
           [3, 4],
           [5, 6]])
    >>> split(data, 3, pad=True)
    array([[1, 2, 3],
           [4, 5, 6]])
    >>> split(data, 4, pad=True)
    array([[1, 2, 3, 4],
           [5, 6, 0, 0]])
    >>> split(data, 5, pad=True)
    array([[1, 2, 3, 4, 5],
           [6, 0, 0, 0, 0]])
    >>> split(data, 6, pad=True)
    array([[1, 2, 3, 4, 5, 6]])
    >>> split(data, 7, pad=True)
    array([[1, 2, 3, 4, 5, 6, 0]])


Overlapping Frames
--------------------------------------------------------------------------------

    >>> split(data, 2, overlap=1)
    array([[1, 2],
           [2, 3],
           [3, 4],
           [4, 5],
           [5, 6]])
    >>> split(data, 3, overlap=1) # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ValueError: ...
    >>> split(data, 3, pad=True, overlap=1)
    array([[1, 2, 3],
           [3, 4, 5],
           [5, 6, 0]])
    >>> split(data, 3, overlap=2)
    array([[1, 2, 3],
           [2, 3, 4],
           [3, 4, 5],
           [4, 5, 6]])
    >>> split(data, 3, overlap=3) # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ValueError: ...


Windows
--------------------------------------------------------------------------------

    >>> data = np.ones(24)
    >>> frames = split(data, 6, window=np.hanning)
    >>> all(all(frame == np.hanning(6)) for frame in frames)
    True


Merging Frames
--------------------------------------------------------------------------------

    >>> frames = [[1, 2, 3], [4, 5, 6], [7, 8, 9]] 
    >>> merge(frames)
    array([1, 2, 3, 4, 5, 6, 7, 8, 9])
    >>> merge(frames, overlap=1)
    array([ 1,  2,  7,  5, 13,  8,  9])
    >>> merge(frames, overlap=2)
    array([ 1,  6, 15, 14,  9])
    >>> merge(frames, window=np.bartlett)
    array([0, 2, 0, 0, 5, 0, 0, 8, 0])
"""


