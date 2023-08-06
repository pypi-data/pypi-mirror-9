"""
..
    Copyright (c) 2014-2015, Magni developers.
    All rights reserved.
    See LICENSE.rst for further information.

Module providing data container classes for MI files.

The classes of this module can be used either directly or indirectly through
the `io` module by loading an MI file.

Routine listings
----------------
Buffer()
    Data class for MI image buffer.
Image()
    Data class for MI image.

See Also
--------
magni.afm.io : MI file loading.

"""

# the name of the present module makes the built-in module 'types' unavailable
from __future__ import absolute_import
from __future__ import division
import types

from magni.imaging.preprocessing import detilt as _detilt
from magni.utils.validation import decorate_validation as _decorate_validation
from magni.utils.validation import validate_generic as _generic
from magni.utils.validation import validate_levels as _levels
from magni.utils.validation import validate_numeric as _numeric


class Buffer():
    """
    Data class for MI image buffer.

    This class contains both buffer specific header lines and the 2D data of
    the buffer.

    Parameters
    ----------
    data : numpy.ndarray
        The data of the buffer represented as a 1D numpy.ndarray.
    hdrs : list or tuple
        The buffer specific header lines.
    width : int
        The width in pixels of the area covered by the buffer.
    height : int
        The height in pixels of the area covered by the buffer.

    Notes
    -----
    See `_image_headers` for a description of the header lines.

    Examples
    --------
    The `__init__` function is implicitly called when loading, for example, the
    MI file provided with the package:

    >>> import os, magni
    >>> path = magni.utils.split_path(magni.__path__[0])[0]
    >>> path = path + 'examples' + os.sep + 'example.mi'
    >>> if os.path.isfile(path):
    ...     mi_file = magni.afm.io.read_mi_file(path)
    ...     mi_buffer = mi_file.get_buffer()[0]

    This buffer can have a number of attributes (stored as header lines in the
    MI file) including the 'bufferLabel' attribute:

    >>> if os.path.isfile(path):
    ...     print(mi_buffer.get_attr('bufferLabel'))
    ... else:
    ...     print('Topography')
    Topography

    The primary purpose of this class is, however, to contain the 2D data of a
    buffer:

    >>> if os.path.isfile(path):
    ...     data = mi_buffer.get_data()
    ...     shape = tuple(int(value) for value in data.shape)
    ...     print('Buffer, Type: {}, Shape: {}'
    ...           .format(str(type(data))[-15:-2], shape))
    ... else:
    ...     print('Buffer, Type: numpy.ndarray, Shape: (256, 256)')
    Buffer, Type: numpy.ndarray, Shape: (256, 256)

    """

    def __init__(self, data, hdrs, width, height):
        @_decorate_validation
        def validate_input():
            _levels('hdrs', (_generic(None, 'explicit collection'),
                             _generic(None, 'explicit collection', len_=2)))

            for i in range(len(hdrs)):
                _generic(('hdrs', i, 0), 'string')

            _numeric('width', 'integer', range_='[1;inf)')
            _numeric('height', 'integer', range_='[1;inf)')
            _numeric('data', ('integer', 'floating'), shape=(height * width,))

        validate_input()

        self._headers = {key: val for key, val in hdrs if key in _image_keys}
        self._data = self.get_attr('bufferRange') * data
        self._data = self._data.reshape(height, width)
        self._data = self._data[::-1, :]

    def get_attr(self, key=None):
        """
        Get a copy of all header lines or a specific header line.

        Parameters
        ----------
        key : str or None, optional
            The name of the header line to retrieve (the default is None, which
            implies retrieving a copy of all header lines).

        Returns
        -------
        value : dict or None
            The value of the specified key, if key is not None. Otherwise, a
            copy of the header lines.

        """

        @_decorate_validation
        def validate_input():
            _generic('key', 'string', value_in=tuple(self._headers.keys()),
                     ignore_none=True)

        validate_input()

        if key is None:
            value = self._headers.copy()
        else:
            value = self._headers[key]

        return value

    def get_data(self, intensity_func=None, intensity_args=()):
        """
        Get the 2D data of the buffer.

        The optional `intensity_func` and `intensity_args` can be used to
        manipulate the intensity of the image before getting the data.

        Parameters
        ----------
        intensity_func : FunctionType, optional
            The handle to the function used to manipulate the image intensity
            (the default is None, which implies that no intensity manipulation
            is used).
        intensity_args : list or tuple, optional
            The arguments that are passed to the `intensity_func` (the default
            is (), which implies that no arguments are passed).

        Returns
        -------
        data : numpy.ndarray
            The 2D data of the buffer.

        """

        @_decorate_validation
        def validate_input():
            _generic('intensity_func', 'function', ignore_none=True)
            _generic('intensity_args', 'explicit collection')

        validate_input()

        data = self._data

        if intensity_func is not None:
            data = intensity_func(data, *intensity_args)

        return data


class Image():
    """
    Data class for MI image.

    This class contains both image specific header lines and the buffers of the
    image.

    Parameters
    ----------
    data : numpy.ndarray
        The data part of the MI image.
    hdrs : list or tuple
        The image specific header lines.

    Notes
    -----
    See `_mi_headers` for a description of the header lines.

    Examples
    --------
    The `__init__` function is implicitly called when loading, for example, the
    MI file provided with the package:

    >>> import os, magni
    >>> path = magni.utils.split_path(magni.__path__[0])[0]
    >>> path = path + 'examples' + os.sep + 'example.mi'
    >>> if os.path.isfile(path):
    ...     image = magni.afm.io.read_mi_file(path)

    This image can have a number of attributes (stored as header lines in the
    MI file) including the 'scanSpeed' attribute:

    >>> if os.path.isfile(path):
    ...     print('{:5.2f}'.format(image.get_attr('scanSpeed')))
    ... else:
    ...     print(' 1.01')
     1.01

    The primary purpose of this class is, however, to contain the buffers of an
    MI image file:

    >>> if os.path.isfile(path):
    ...     buffers = image.get_buffer()
    ...     for b in buffers[0:5:2]:
    ...         print('Buffer: {}'.format(b.get_attr('bufferLabel')))
    ... else:
    ...     for b in ('Topography', 'Deflection', 'Friction'):
    ...         print('Buffer: {}'.format(b))
    Buffer: Topography
    Buffer: Deflection
    Buffer: Friction

    """

    def __init__(self, data, hdrs):
        @_decorate_validation
        def validate_input():
            _numeric('data', ('integer', 'floating'), shape=(-1,))
            _levels('hdrs', (_generic(None, 'explicit collection'),
                             _generic(None, 'explicit collection', len_=2)))

            for i in range(len(hdrs)):
                _generic(('hdrs', i, 0), 'string')

        validate_input()

        end = [hdr[0] for hdr in hdrs].index(_image_keys[0])
        self._headers = {key: val for key, val in hdrs[:end] + [hdrs[-1]]
                         if key in _mi_keys}

        self._buffers = []
        width = self.get_attr('xPixels')
        height = self.get_attr('yPixels')
        size = width * height
        bufs = []

        for i in range(end, len(hdrs) - 1):
            if hdrs[i][0] == _image_keys[0]:
                bufs.append([])

            bufs[-1].append(hdrs[i])

        for i in range(len(bufs)):
            buf = data[i * size:(i + 1) * size]
            self._buffers.append(Buffer(buf, bufs[i], width, height))

    def get_attr(self, key=None):
        """
        Get a copy of all header lines or a specific header line.

        Parameters
        ----------
        key : str or None, optional
            The name of the header line to retrieve (the default is None, which
            implies retrieving a copy of all header lines).

        Returns
        -------
        value : dict or None
            The value of the specified key, if key is not None. Otherwise, a
            copy of the header lines.

        """

        @_decorate_validation
        def validate_input():
            _generic('key', 'string', value_in=tuple(self._headers.keys()),
                     ignore_none=True)

        validate_input()

        if key is None:
            value = self._headers.copy()
        else:
            value = self._headers[key]

        return value

    def get_buffer(self, key=None):
        """
        Get all buffers or a specific buffer.

        Parameters
        ----------
        key : str or None, optional
            The name of the buffer to retrieve (the default is None, which
            implies retrieving all buffers).

        Returns
        -------
        value : dict or None
            The buffer of the specified key, if key is not None. Otherwise, a
            dict with all the buffers.

        """

        @_decorate_validation
        def validate_input():
            keys = tuple(buffer_.get_attr('bufferLabel')
                         for buffer_ in self._buffers)
            _generic('key', 'string', value_in=keys, ignore_none=True)

        validate_input()

        if key is None:
            buf = self._buffers[:]
        else:
            buf = [buffer for buffer in self._buffers
                   if buffer.get_attr('bufferLabel') == key]

            if len(buf) == 1:
                buf = buf[0]

        return buf


_mi_headers = (
    ('fileType      ', 'Specifies if it is Image or plot file'),
    ('version       ', 'Software version'),
    ('dateAcquired  ', 'Date and time scan started'),
    ('dateModified  ', 'Date and time data saved'),
    ('comment       ', ''),
    ('mode          ', 'ModeAFM = Acquired in contact AFM'),
    ('xSensitivity  ', 'X sensitivity for scanner (m/V)'),
    ('xNonlinearity ', 'X non-linearity for scanner'),
    ('xHysteresis   ', 'X hysteresis for scanner (% scan size)'),
    ('ySensitivity  ', 'Y sensitivity for scanner (m/V)'),
    ('yNonlinearity ', 'Y non-linearity for scanner'),
    ('yHysteresis   ', 'Y hysteresis for scanner (% scan size)'),
    ('zSensitivity  ', 'Z sensitivity for scanner (m/V)'),
    ('reverseX      ', 'Reverse X polarity for scanner'),
    ('reverseY      ', 'Reverse Y polarity for scanner'),
    ('reverseZ      ', 'Reverse Z polarity for scanner'),
    ('xDacRange     ', 'X output range for controller (V)'),
    ('yDacRange     ', 'Y output range for controller (V)'),
    ('zDacRange     ', 'Z output range for controller (V)'),
    ('xPixels       ', 'Columns in image'),
    ('yPixels       ', 'Rows in image'),
    ('xOffset       ', 'X offset in total scan area'),
    ('yOffset       ', 'Y offset in total scan area'),
    ('xLength       ', 'X scan Size (m)'),
    ('yLength       ', 'Y scan Size (m)'),
    ('scanUp        ', 'Scanning up = TRUE, down = FALSE'),
    ('scanSpeed     ', 'Fast scan speed (lines/sec or Hz)'),
    ('scanAngle     ', 'Scan angle (degrees)'),
    ('servoSetpoint ', 'Z servo setpoint (V)'),
    ('biasSample    ', 'Bias applied to sample (TRUE), tip (FALSE)'),
    ('bias          ', 'Bias voltage (V)'),
    ('servoIGain    ', 'Z servo integral gain'),
    ('servoPGain    ', 'Z servo proportional gain'),
    ('servoRange    ', 'Z servo range (m)'),
    ('servoInputGain', 'Z servo input gain'),
    ('acFrequency   ', 'AC Mode frequency (Hz)'),
    ('acDrive       ', 'AC Mode drive (%)'),
    ('acGain        ', 'AC Mode input gain'),
    ('acMac         ', 'AC Mode MAC (TRUE), AAC (FALSE)'),
    ('acACMode      ', 'AC Mode AC (TRUE), contact (FALSE)'),
    ('snapFileName  ', 'Names of snap files'),
    ('snapAfmPos    ', 'XY-positions of snap images (m)'),
    ('snapAfmOpacity', 'Snap opacities in range [0, 100]%'),
    ('snapResolution', 'Snap resolutions (pixels)'),
    ('snapSens      ', 'Optical X and Y snap sensitivities (m/pixel)'),
    ('snapROI       ', 'ROI for each snap image'),
    ('snapObjective ', 'Objective names for each snap image'),
    ('snapName      ', 'Snap names'),
    ('tipX          ', 'Tip X position'),
    ('tipY          ', 'Tip Y position'),
    ('data          ', 'Data'))
_mi_headers = tuple((key.strip(), descr) for key, descr in _mi_headers)
_mi_keys = [hdr[0] for hdr in _mi_headers]

_image_headers = (
    ('bufferLabel   ', 'First buffer label'),
    ('trace         ', 'First buffer trace (TRUE), retrace (FALSE)'),
    ('bufferUnit    ', 'First buffer unit'),
    ('bufferRange   ', 'First buffer range (bufferUnit unit)'),
    # the following headers are not part of the format specification
    ('DisplayOffset ', 'First buffer display offset'),
    ('DisplayRange  ', 'First buffer display range'),
    ('filter        ', 'First buffer plane flattening order'))
_image_headers = tuple((key.strip(), descr) for key, descr in _image_headers)
_image_keys = [hdr[0] for hdr in _image_headers]
