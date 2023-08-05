#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2010, 2011, 2012, 2013, 2014.

# SMHI,
# Folkborgsvägen 1,
# Norrköping,
# Sweden

# Author(s):

#   Martin Raspaud <martin.raspaud@smhi.se>
#   Adam Dybbroe <adam.dybbroe@smhi.se>

# This file is part of mpop.

# mpop is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.

# mpop is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# mpop.  If not, see <http://www.gnu.org/licenses/>.

"""This module defines satellite instrument channels as a generic class, to be
inherited when needed.
"""
import copy

import numpy as np
import logging

LOG = logging.getLogger(__name__)

try:
    from pyorbital.astronomy import sun_zenith_angle as sza
except ImportError:
    sza = None


class NotLoadedError(Exception):

    """Exception to be raised when attempting to use a non-loaded channel.
    """
    pass


class GenericChannel(object):

    """This is an abstract channel class. It can be a super class for
    calibrated channels data or more elaborate channels such as cloudtype or
    CTTH.
    """

    def __init__(self, name=None):
        object.__init__(self)

        # Channel name
        if name is not None and not isinstance(name, str):
            raise TypeError("Channel name must be a string, or None")
        self.name = name

        # Channel resolution, in meters.
        self.resolution = None

        # ID of the area on which the channel is defined.
        self.area_id = None

        # Area on which the channel is defined.
        self.area_def = None
        self.info = {}

    def __cmp__(self, ch2):
        if(isinstance(ch2, str)):
            return cmp(self.name, ch2)
        elif(ch2.name is not None and
             self.name is not None and
             ch2.name[0] == "_" and
             self.name[0] != "_"):
            return -1
        elif(ch2.name is not None and
             self.name is not None and
             ch2.name[0] != "_" and
             self.name[0] == "_"):
            return 1
        else:
            return cmp(self.name, ch2.name)

    def _get_area(self):
        """Getter for area.
        """
        return self.area_def or self.area_id

    def _set_area(self, area):
        """Setter for area.
        """
        if (area is None):
            self.area_def = None
            self.area_id = None
        elif(isinstance(area, str)):
            self.area_id = area
        else:
            try:
                dummy = area.area_extent
                dummy = area.x_size
                dummy = area.y_size
                dummy = area.proj_id
                dummy = area.proj_dict
                self.area_def = area
            except AttributeError:
                try:
                    dummy = area.lons
                    dummy = area.lats
                    self.area_def = area
                    self.area_id = None
                except AttributeError:
                    raise TypeError("Malformed area argument. "
                                    "Should be a string or an area object.")

    area = property(_get_area, _set_area)


class Channel(GenericChannel):

    """This is the satellite channel class. It defines satellite channels as a
    container for calibrated channel data.

    The *resolution* sets the resolution of the channel, in meters. The
    *wavelength_range* is a triplet, containing the lowest-, center-, and
    highest-wavelength values of the channel. *name* is simply the given name
    of the channel, and *data* is the data it should hold.
    """

    def __init__(self,
                 name=None,
                 resolution=0,
                 wavelength_range=[-np.inf, -np.inf, -np.inf],
                 data=None,
                 calibration_unit=None):

        GenericChannel.__init__(self, name)

        self._data = None
        self.wavelength_range = None

        if(name is None and
           wavelength_range == [-np.inf, -np.inf, -np.inf]):
            raise ValueError("Cannot define a channel with neither name "
                             "nor wavelength range.")

        if not isinstance(resolution, (int, float)):
            raise TypeError("Resolution must be an integer number of meters.")

        self.resolution = resolution

        if(not isinstance(wavelength_range, (tuple, list, set)) or
           len(wavelength_range) != 3 or
           not isinstance(wavelength_range[0], float) or
           not isinstance(wavelength_range[1], float) or
           not isinstance(wavelength_range[2], float)):
            raise TypeError("Wavelength_range should be a triplet of floats.")
        elif(not (wavelength_range[0] <= wavelength_range[1]) or
             not (wavelength_range[1] <= wavelength_range[2])):
            raise ValueError("Wavelength_range should be a sorted triplet.")

        self.wavelength_range = list(wavelength_range)
        self.unit = calibration_unit
        self.data = data

    def get_reflectance(self, tb11, sun_zenith=None, tb13_4=None):
        """Get the reflectance part of an NIR channel"""

        try:
            from pyspectral.near_infrared_reflectance import Calculator
        except ImportError:
            LOG.info("Couldn't load pyspectral")

        # Check the wavelength, and if outside 3-4 microns this functionality
        # doesn't give any meaning and should not be supported
        if (self.wavelength_range[1] < 3.0 or self.wavelength_range[1] > 4.0):
            LOG.warning("Deriving the near infrared reflectance" +
                        " of a band that is outside the 3-4 micron range" +
                        " is not supported!\n\tWill do nothing...")
            return

        # Check if the sun-zenith angle was provided:
        if sun_zenith is None:
            lonlats = self.area.get_lonlats()
            sun_zenith = sza(self.info['time'], lonlats[0], lonlats[1])

        try:
            refl39 = Calculator(self.info['satname'], self.info['satnumber'],
                                self.info['instrument_name'], self.name)
        except NameError:
            LOG.warning("pyspectral missing!")
            return

        return refl39.reflectance_from_tbs(sun_zenith, self.data,
                                           tb11, tb13_4)

    def __cmp__(self, ch2, key=0):
        if(isinstance(ch2, str)):
            return cmp(self.name, ch2)
        elif(ch2.name is not None and
             self.name is not None and
             ch2.name[0] == "_" and
             self.name[0] != "_"):
            return -1
        elif(ch2.name is not None and
             self.name is not None and
             ch2.name[0] != "_" and
             self.name[0] == "_"):
            return 1
        else:
            res = cmp(abs(self.wavelength_range[1] - key),
                      abs(ch2.wavelength_range[1] - key))
            if res == 0:
                return cmp(self.name, ch2.name)
            else:
                return res

    def __str__(self):
        if self.shape is not None:
            return ("'%s: (%.3f,%.3f,%.3f)μm, shape %s, resolution %sm'" %
                    (self.name,
                     self.wavelength_range[0],
                     self.wavelength_range[1],
                     self.wavelength_range[2],
                     self.shape,
                     self.resolution))
        else:
            return ("'%s: (%.3f,%.3f,%.3f)μm, resolution %sm, not loaded'" %
                    (self.name,
                     self.wavelength_range[0],
                     self.wavelength_range[1],
                     self.wavelength_range[2],
                     self.resolution))

    def is_loaded(self):
        """Tells if the channel contains loaded data.
        """
        return self._data is not None

    def check_range(self, min_range=1.0):
        """Check that the data of the channels has a definition domain broader
        than *min_range* and return the data, otherwise return zeros.
        """
        if not self.is_loaded():
            raise ValueError("Cannot check range of an non-loaded channel")

        if not isinstance(min_range, (float, int)):
            raise TypeError("Min_range must be a single number.")

        if isinstance(self._data, np.ma.core.MaskedArray):
            if self._data.mask.all():
                return self._data

        if((self._data.max() - self._data.min()) < min_range):
            return np.ma.zeros(self.shape)
        else:
            return self._data

    def show(self):
        """Display the channel as an image.
        """
        if not self.is_loaded():
            raise ValueError("Channel not loaded, cannot display.")

        from PIL import Image as pil

        data = ((self._data - self._data.min()) * 255.0 /
                (self._data.max() - self._data.min()))
        if isinstance(data, np.ma.core.MaskedArray):
            img = pil.fromarray(np.array(data.filled(0), np.uint8))
        else:
            img = pil.fromarray(np.array(data, np.uint8))
        img.show()

    def as_image(self, stretched=True):
        """Return the channel as a :class:`mpop.imageo.geo_image.GeoImage`
        object. The *stretched* argument set to False allows the data to remain
        untouched (as opposed to crude stretched by default to obtain the same
        output as :meth:`show`).
        """
        from mpop.imageo.geo_image import GeoImage

        img = GeoImage(self._data, self.area, None)
        if stretched:
            img.stretch("crude")
        return img

    def project(self, coverage_instance):
        """Make a projected copy of the current channel using the given
        *coverage_instance*.

        See also the :mod:`mpop.projector` module.
        """
        res = Channel(name=self.name,
                      resolution=self.resolution,
                      wavelength_range=self.wavelength_range,
                      data=None,
                      calibration_unit=self.unit)
        res.area = coverage_instance.out_area
        res.info = self.info
        if self.is_loaded():
            LOG.info("Projecting channel %s (%fμm)..."
                     % (self.name, self.wavelength_range[1]))
            data = coverage_instance.project_array(self._data)
            res.data = data
            return res
        else:
            raise NotLoadedError("Can't project, channel %s (%fμm) not loaded."
                                 % (self.name, self.wavelength_range[1]))

    def get_data(self):
        """Getter for channel data.
        """
        return self._data

    def set_data(self, data):
        """Setter for channel data.
        """
        if data is None:
            del self._data
            self._data = None
        elif isinstance(data, (np.ndarray, np.ma.core.MaskedArray)):
            self._data = data
        else:
            raise TypeError("Data must be a numpy (masked) array.")

    data = property(get_data, set_data)

    @property
    def shape(self):
        """Shape of the channel.
        """
        if self.data is None:
            return None
        else:
            return self.data.shape

    def sunzen_corr(self, time_slot, lonlats=None, limit=80., mode='cos'):
        '''Perform Sun zenith angle correction for the channel at
        *time_slot* (datetime.datetime() object) and return the
        corrected channel.  The parameter *limit* can be used to set
        the maximum zenith angle for which the correction is
        calculated.  For larger angles, the correction is the same as
        at the *limit* (default: 80.0 degrees).  Coordinate values can
        be given as a 2-tuple or a two-element list *lonlats* of numpy
        arrays; if None, the coordinates will be read from the channel
        data.  Parameter *mode* is a placeholder for other possible
        illumination corrections. The name of the new channel will be
        *original_chan.name+'_SZC'*, eg. "VIS006_SZC".  This name is
        also stored to the info dictionary of the originating channel.
        '''

        import mpop.tools

        try:
            from pyorbital import astronomy
        except ImportError:
            LOG.warning("Could not load pyorbital.astronomy")
            return None

        if lonlats is None or len(lonlats) != 2:
            # Read coordinates
            LOG.debug("No valid coordinates given, reading from the "
                      "channel data")
            lons, lats = self.area.get_lonlats()
        else:
            lons, lats = lonlats

        # Calculate Sun zenith angles and the cosine
        cos_zen = astronomy.cos_zen(time_slot, lons, lats)

        # Copy the channel
        new_ch = copy.deepcopy(self)

        # Set the name
        new_ch.name += '_SZC'

        if mode == 'cos':
            new_ch.data = mpop.tools.sunzen_corr_cos(new_ch.data,
                                                     cos_zen, limit=limit)
        else:
            # Placeholder for other correction methods
            pass

        # Add information about the corrected version to original
        # channel
        self.info["sun_zen_corrected"] = self.name + '_SZC'

        return new_ch

    # Arithmetic operations on channels.

    def __pow__(self, other):
        return Channel(name="new", data=self.data ** other)

    def __rpow__(self, other):
        return Channel(name="new", data=self.data ** other)

    def __mul__(self, other):
        return Channel(name="new", data=self.data * other)

    def __rmul__(self, other):
        return Channel(name="new", data=self.data * other)

    def __add__(self, other):
        return Channel(name="new", data=self.data + other)

    def __radd__(self, other):
        return Channel(name="new", data=self.data + other)

    def __sub__(self, other):
        return Channel(name="new", data=self.data - other)

    def __rsub__(self, other):
        return Channel(name="new", data=self.data - other)

    def __div__(self, other):
        return Channel(name="new", data=self.data / other)

    def __rdiv__(self, other):
        return Channel(name="new", data=self.data / other)

    def __neg__(self):
        return Channel(name="new", data=-self.data)

    def __abs__(self):
        return Channel(name="new", data=abs(self.data))
