#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2011, 2012, 2013, 2014, 2015.

# Author(s):

#
#   Adam Dybbroe <adam.dybbroe@smhi.se>
#   Kristian Rune Larsen <krl@dmi.dk>
#   Lars Ørum Rasmussen <ras@dmi.dk>
#   Martin Raspaud <martin.raspaud@smhi.se>
#

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

"""Interface to VIIRS SDR format

Format documentation:
http://npp.gsfc.nasa.gov/science/sciencedocuments/082012/474-00001-03_CDFCBVolIII_RevC.pdf

"""
import os.path
from ConfigParser import ConfigParser
from datetime import datetime, timedelta

import numpy as np
import h5py
import hashlib
import logging

from mpop import CONFIG_PATH
from mpop.utils import strftime

NO_DATE = datetime(1958, 1, 1)
EPSILON_TIME = timedelta(days=2)
VIIRS_MBAND_GRANULE_SIZE = (768, 3200)
VIIRS_DNB_GRANULE_SIZE = (768, 4064)
VIIRS_IBAND_GRANULE_SIZE = (768 * 2, 3200 * 2)

VIIRS_IR_BANDS = ('M16', 'M15', 'M14', 'M13', 'M12', 'I5', 'I4')
VIIRS_VIS_BANDS = ('M1', 'M2', 'M3', 'M4', 'M5', 'M6',
                   'M7', 'M8', 'M9', 'M10', 'M11',
                   'I1', 'I2', 'I3')
VIIRS_DNB_BANDS = ('DNB', )

logger = logging.getLogger(__name__)


class HDF5MetaData(object):

    """

    Small class for inspecting a HDF5 file and retrieve its metadata/header
    data. It is developed for JPSS/NPP data but is really generic and should
    work on most other hdf5 files.

    Supports

    """

    def __init__(self, filename):
        self.metadata = {}
        self.filename = filename
        if not os.path.exists(filename):
            raise IOError("File %s does not exist!" % filename)

    def read(self):
        h5f = h5py.File(self.filename, 'r')
        h5f.visititems(self.collect_metadata)
        self._collect_attrs('/', h5f.attrs)
        h5f.close()
        return self

    def _collect_attrs(self, name, attrs):
        for key, value in attrs.iteritems():
            value = np.squeeze(value)
            if issubclass(value.dtype.type, str):
                self.metadata["%s/attr/%s" % (name, key)] = str(value)
            else:
                self.metadata["%s/attr/%s" % (name, key)] = value

    def collect_metadata(self, name, obj):
        if isinstance(obj, h5py.Dataset):
            self.metadata["%s/shape" % name] = obj.shape
        self._collect_attrs(name, obj.attrs)

    def __getitem__(self, key):

        long_key = None
        for mkey in self.metadata.keys():
            if mkey.endswith(key):
                if long_key is not None:
                    raise KeyError("Multiple keys called %s" % key)
                long_key = mkey
                # Test this to be able to read SDR files with several granules
                # in one file (Matias' files)
                break
        return self.metadata[long_key]

    def keys(self):
        return self.metadata.keys()

    def get_data_keys(self):

        data_keys = []
        for key in self.metadata.keys():
            if key.endswith("/shape"):
                data_key = key.split("/shape")[0]
                data_keys.append(data_key)
        return data_keys


class NPPMetaData(HDF5MetaData):

    def _parse_npp_datatime(self, datestr, timestr):
        time_val = datetime.strptime(datestr + timestr, '%Y%m%d%H%M%S.%fZ')
        if abs(time_val - NO_DATE) < EPSILON_TIME:
            raise ValueError("Datetime invalid %s " % time_val)
        return time_val

    def get_ring_lonlats(self):
        return self['G-Ring_Longitude'], self['G-Ring_Latitude']

    def get_begin_time(self):
        return self._parse_npp_datatime(self['AggregateBeginningDate'],
                                        self['AggregateBeginningTime'])

    def get_end_time(self):
        return self._parse_npp_datatime(self['AggregateEndingDate'],
                                        self['AggregateEndingTime'])

    def get_begin_orbit_number(self):
        return int(self['AggregateBeginningOrbitNumber'])

    def get_end_orbit_number(self):
        return int(self['AggregateEndingOrbitNumber'])

    def get_geofilname(self):
        return self['N_GEO_Ref']

    def get_shape(self):

        shape = self['Radiance/shape']
        band = self['Band_ID']
        if band[0] == 'M':
            # if shape != VIIRS_MBAND_GRANULE_SIZE:
            if ((shape[0] % VIIRS_MBAND_GRANULE_SIZE[0]) != 0 and
                    (shape[1] % VIIRS_MBAND_GRANULE_SIZE[1]) != 0):
                raise ValueError(
                    "Unsupported granule size %s for %s" % (shape, band))
        elif band == "DNB":
            if ((shape[0] % VIIRS_DNB_GRANULE_SIZE[0]) != 0 and
                    (shape[1] % VIIRS_MBAND_GRANULE_SIZE[1]) != 0):
                raise ValueError(
                    "Unsupported granule size %s for %s" % (shape, band))
        elif band[0] == "I":
            if ((shape[0] % VIIRS_IBAND_GRANULE_SIZE[0] != 0) and
                    (shape[1] % VIIRS_IBAND_GRANULE_SIZE[1] != 0)):
                raise ValueError(
                    "Unsupported granule size %s for %s" % (shape, band))

        return shape

    def get_band_description(self):

        band = self['Band_ID']

        for band_desc in ('I', 'M', 'DNB', "N/A"):
            if band.startswith(band_desc):
                if band_desc == 'N/A':
                    return 'DNB'
                return band_desc
        return None

    def _band_data_keys(self, data_type):
        """
        :param data_type: Reflectance, Radiance or BrightnessTemperature
        :type data_type: string
        :returns: HDF5 data key and scale factor keys in a two element tuple

        """
        data_key = None
        factors_keys = None
        for key in self.get_data_keys():
            if key.endswith(data_type):
                data_key = key
                factors_keys = key + "Factors"

        return (data_key, factors_keys)

    def get_reflectance_keys(self):
        return self._band_data_keys("Reflectance")

    def get_radiance_keys(self):
        return self._band_data_keys("Radiance")

    def get_brightness_temperature_keys(self):
        return self._band_data_keys("BrightnessTemperature")

    def get_unit(self, calibrate=1):

        band = self['Band_ID']
        if calibrate == 2 and band not in VIIRS_DNB_BANDS:
            return "W m-2 um-1 sr-1"

        if band in VIIRS_IR_BANDS:
            return "K"
        elif band in VIIRS_VIS_BANDS:
            return '%'
        elif band in VIIRS_DNB_BANDS:
            return 'W m-2 sr-1'

        return None


#
#
# http://yloiseau.net/articles/DesignPatterns/flyweight/
class GeolocationFlyweight(object):

    def __init__(self, cls):
        self._cls = cls
        self._instances = dict()

    def __call__(self, *args, **kargs):
        """
        we assume that this is only used for the gelocation object,
        filenames are listed in the second argument

        """
        return self._instances.setdefault(tuple(args[1]),
                                          self._cls(*args, **kargs))

    def clear_cache(self):
        del self._instances
        self._instances = dict()


@GeolocationFlyweight
class ViirsGeolocationData(object):

    def __init__(self, shape, filenames):
        self.filenames = filenames
        self.longitudes = None
        self.shape = shape
        self.latitudes = None
        self.mask = None

    def read(self):
        """
        Read longitudes and latitudes from geo filenames and assemble
        """

        if self.longitudes is not None:
            return self

        self.longitudes = np.empty(self.shape,
                                   dtype=np.float32)
        self.latitudes = np.empty(self.shape,
                                  dtype=np.float32)
        self.mask = np.zeros(self.shape,
                             dtype=np.bool)

        granule_length = self.shape[0] / len(self.filenames)

        for index, filename in enumerate(self.filenames):

            swath_index = index * granule_length
            y0_ = swath_index
            y1_ = swath_index + granule_length

            get_lonlat_into(filename,
                            self.longitudes[y0_:y1_, :],
                            self.latitudes[y0_:y1_, :],
                            self.mask[y0_:y1_, :])
        self.longitudes = np.ma.array(self.longitudes,
                                      mask=self.mask,
                                      copy=False)
        self.latitudes = np.ma.array(self.latitudes,
                                     mask=self.mask,
                                     copy=False)
        logger.debug("Geolocation read in for... " + str(self))
        return self


# ------------------------------------------------------------------------------

def _get_invalid_info(granule_data):
    """Get a detailed report of the missing data.
        N/A: not applicable
        MISS: required value missing at time of processing
        OBPT: onboard pixel trim (overlapping/bow-tie pixel removed during
            SDR processing)
        OGPT: on-ground pixel trim (overlapping/bow-tie pixel removed
            during EDR processing)
        ERR: error occurred during processing / non-convergence
        ELINT: ellipsoid intersect failed / instrument line-of-sight does
            not intersect the Earth’s surface
        VDNE: value does not exist / processing algorithm did not execute
        SOUB: scaled out-of-bounds / solution not within allowed range
    """
    if issubclass(granule_data.dtype.type, np.integer):
        msg = ("na:" + str((granule_data == 65535).sum()) +
               " miss:" + str((granule_data == 65534).sum()) +
               " obpt:" + str((granule_data == 65533).sum()) +
               " ogpt:" + str((granule_data == 65532).sum()) +
               " err:" + str((granule_data == 65531).sum()) +
               " elint:" + str((granule_data == 65530).sum()) +
               " vdne:" + str((granule_data == 65529).sum()) +
               " soub:" + str((granule_data == 65528).sum()))
    if issubclass(granule_data.dtype.type, np.floating):
        msg = ("na:" + str((granule_data == -999.9).sum()) +
               " miss:" + str((granule_data == -999.8).sum()) +
               " obpt:" + str((granule_data == -999.7).sum()) +
               " ogpt:" + str((granule_data == -999.6).sum()) +
               " err:" + str((granule_data == -999.5).sum()) +
               " elint:" + str((granule_data == -999.4).sum()) +
               " vdne:" + str((granule_data == -999.3).sum()) +
               " soub:" + str((granule_data == -999.2).sum()))
    return msg


class ViirsBandData(object):

    """Placeholder for the VIIRS M&I-band data.
    Reads the SDR data - one hdf5 file for each band.
    Not yet considering the Day-Night Band
    """

    def __init__(self, filenames, calibrate=1):
        self.begin_time = 0
        self.end_time = 0
        self.orbit_begin = 0
        self.orbit_end = 0
        self.band_id = 'unknown'
        self.data = None
        self.mask = None
        self.raw_data = None
        self.scale = 1.0    # gain
        self.offset = 0.0   # intercept
        self.filenames = sorted(filenames)
        self.units = 'unknown'
        self.geo_filenames = []
        self.calibrate = calibrate

        self.data = None
        self.geolocation = None

        self.band_desc = None
        self.band_uid = None
        self.metadata = []

    def read(self):
        self._read_metadata()

        logger.debug("Shape of data: " + str(self.raw_data.shape))

        self._read_data()

        return self

    def _read_metadata(self):

        logger.debug("Filenames: " + str(self.filenames))

        for fname in self.filenames:
            logger.debug("Get and append metadata from file: " + str(fname))
            md = NPPMetaData(fname).read()
            self.metadata.append(md)
            self.geo_filenames.append(md.get_geofilname())
            # Check if the geo-filenames actually exists:
            # geofilename = md.get_geofilname()
            # if os.path.exists(geofilename):
            #     self.geo_filenames.append(geofilename)
            # else:
            #     logger.warning("Geo file defined in metadata header " +
            #                    "does not exist: " + str(geofilename))

        #
        # initiate data arrays
        granule_length, swath_width = self.metadata[0].get_shape()
        shape = (granule_length * len(self.metadata), swath_width)

        #self.data = np.ma.array(np.zeros(shape, dtype=np.float32), fill_value=0)
        self.raw_data = np.zeros(shape, dtype=np.float32)
        self.mask = np.zeros(shape, dtype=np.bool)
        self.orbit_begin = self.metadata[0].get_begin_orbit_number()
        self.orbit_end = self.metadata[-1].get_end_orbit_number()
        self.begin_time = self.metadata[0].get_begin_time()
        self.end_time = self.metadata[-1].get_end_time()

        self.units = self.metadata[0].get_unit(self.calibrate)
        self.band_desc = self.metadata[0].get_band_description()

        self.band_id = self.metadata[0]['Band_ID']
        if self.band_id == "N/A":
            self.band_id = "DNB"

    def _read_data(self):
        """Read one VIIRS M- or I-band channel: Data and attributes (meta data)

        - *calibrate* set to 1 (default) returns reflectances for visual bands,
           tb for ir bands, and radiance for dnb.

        - *calibrate* set to 2 returns radiances.
        """

        granule_length, swath_width = self.metadata[0].get_shape()

        for index, md in enumerate(self.metadata):
            h5f = h5py.File(md.filename, 'r')

            # find appropiate band data to insert
            data_key = None
            factors_key = None
            if self.calibrate == 1:
                data_key, factors_key = md.get_reflectance_keys()
                if data_key is None:
                    data_key, factors_key = md.get_brightness_temperature_keys()
                    logger.debug("data and factors keys: " +
                                 str(data_key) + str(factors_key))
                # handle dnb data
                if data_key is None and self.band_id == "DNB":
                    data_key, factors_key = md.get_radiance_keys()

            elif self.calibrate == 2:
                data_key, factors_key = md.get_radiance_keys()

            #
            # get granule data and scale and offset values
            try:
                granule_factors_data = h5f[factors_key].value
            except KeyError:
                #
                # We can't find the factors this must be DNB
                # if self.band_id != "DNB":
                #     raise
                # We can't find the factors, so this must be the DNB or the M13
                # band:
                logger.debug("Band id = " + str(self.band_id))

                if self.band_id != "DNB" and self.band_id != "M13":
                    raise
                if self.band_id == "DNB":
                    # The unit is W/sr cm-2 in the file! but we need 'W sr-1
                    # m-2'
                    granule_factors_data = (10000., 0.)
                else:
                    # M13 is stored in floats with no scale or offset:
                    granule_factors_data = (1., 0.)

            granule_data = h5f[data_key].value

            self.scale, self.offset = granule_factors_data[0:2]

            # The VIIRS reflectances are between 0 and 1.
            # mpop standard is '%'
            if self.units == '%':
                # To get reflectances in percent!
                self.scale *= np.int8(100)
                self.offset *= np.int8(100)

            swath_index = index * granule_length
            y0_ = swath_index
            y1_ = swath_index + granule_length

            self.raw_data[y0_:y1_, :] = granule_data
            self.raw_data[y0_:y1_, :] *= self.scale
            self.raw_data[y0_:y1_, :] += self.offset
            logger.debug("dtype(granule_data) = " + str(granule_data.dtype))

            # Masking spurious data
            # according to documentation, mask integers >= 65328, floats <=
            # -999.3

            if issubclass(granule_data.dtype.type, np.integer):
                self.mask[y0_:y1_, :] = granule_data >= 65528
            if issubclass(granule_data.dtype.type, np.floating):
                self.mask[y0_:y1_, :] = granule_data < -999.2
            logger.debug("%s", _get_invalid_info(granule_data))

            # Is it necessary to mask negatives?
            #self.mask[y0_:y1_, :] |= self.raw_data[y0_:y1_, :] < 0

            h5f.close()

        self.data = np.ma.array(self.raw_data, mask=self.mask, copy=False)

        self.band_uid = self.band_desc + hashlib.sha1(self.mask).hexdigest()


    def read_lonlat(self, geofilepaths=None, geodir=None):

        if geofilepaths is None:
            if geodir is None:
                geodir = os.path.dirname(self.metadata[0].filename)

            logger.debug("Geo-files = " + str(self.geo_filenames))
            geofilepaths = [os.path.join(geodir, geofilepath)
                            for geofilepath in self.geo_filenames]

        logger.debug("Geo-files = " + str(geofilepaths))
        self.geolocation = ViirsGeolocationData(self.data.shape,
                                                geofilepaths).read()


# ------------------------------------------------------------------------------
from mpop.plugin_base import Reader


class ViirsSDRReader(Reader):
    pformat = "viirs_sdr"

    def __init__(self, *args, **kwargs):
        Reader.__init__(self, *args, **kwargs)

    def load(self, satscene, calibrate=1, time_interval=None, area=None, filename=None, **kwargs):
        """Read viirs SDR reflectances and Tbs from file and load it into
        *satscene*.
        """
        if satscene.instrument_name != "viirs":
            raise ValueError("Wrong instrument, expecting viirs")

        if kwargs:
            logger.warning(
                "Unsupported options for viirs reader: %s", str(kwargs))

        conf = ConfigParser()
        conf.read(os.path.join(CONFIG_PATH, satscene.fullname + ".cfg"))
        options = {}
        for option, value in conf.items(satscene.instrument_name + "-level2",
                                        raw=True):
            options[option] = value

        band_list = [s.name for s in satscene.channels]
        chns = satscene.channels_to_load & set(band_list)
        if len(chns) == 0:
            return

        if time_interval:
            time_start, time_end = time_interval
        else:
            time_start, time_end = satscene.time_slot, None

        import glob

        if "filename" not in options:
            raise IOError("No filename given, cannot load")

        values = {"orbit": satscene.orbit,
                  "satname": satscene.satname,
                  "instrument": satscene.instrument_name,
                  "satellite": satscene.satname
                  #"satellite": satscene.fullname
                  }

        file_list = []
        if filename is not None:
            if not isinstance(filename, (list, set, tuple)):
                filename = [filename]
            geofile_list = []
            for fname in filename:
                if os.path.basename(fname).startswith("SV"):
                    file_list.append(fname)
                elif os.path.basename(fname).startswith("G"):
                    geofile_list.append(fname)
                else:
                    logger.info("Unrecognized SDR file: %s", fname)
            if file_list:
                directory = os.path.dirname(file_list[0])
            if geofile_list:
                geodirectory = os.path.dirname(geofile_list[0])

        if not file_list:
            filename_tmpl = strftime(
                satscene.time_slot, options["filename"]) % values

            directory = strftime(satscene.time_slot, options["dir"]) % values

            if not os.path.exists(directory):
                #directory = globify(options["dir"]) % values
                directory = globify(
                    strftime(satscene.time_slot, options["dir"])) % values
                logger.debug(
                    "Looking for files in directory " + str(directory))
                directories = glob.glob(directory)
                if len(directories) > 1:
                    raise IOError("More than one directory for npp scene... " +
                                  "\nSearch path = %s\n\tPlease check npp.cfg file!" % directory)
                elif len(directories) == 0:
                    raise IOError("No directory found for npp scene. " +
                                  "\nSearch path = %s\n\tPlease check npp.cfg file!" % directory)
                else:
                    directory = directories[0]

            file_list = glob.glob(os.path.join(directory, filename_tmpl))

            # Only take the files in the interval given:
            logger.debug("Number of files before segment selection: "
                         + str(len(file_list)))
            for fname in file_list:
                if os.path.basename(fname).startswith("SVM14"):
                    logger.debug("File before segmenting: "
                                 + os.path.basename(fname))
            file_list = _get_swathsegment(
                file_list, time_start, time_end, area)
            logger.debug("Number of files after segment selection: "
                         + str(len(file_list)))

            for fname in file_list:
                if os.path.basename(fname).startswith("SVM14"):
                    logger.debug("File after segmenting: "
                                 + os.path.basename(fname))

            logger.debug("Template = " + str(filename_tmpl))

            # 22 VIIRS bands (16 M-bands + 5 I-bands + DNB)
            if len(file_list) % 22 != 0:
                logger.warning("Number of SDR files is not divisible by 22!")
            if len(file_list) == 0:
                logger.debug(
                    "File template = " + str(os.path.join(directory, filename_tmpl)))
                raise IOError("No VIIRS SDR file matching!: " +
                              "Start time = " + str(time_start) +
                              "  End time = " + str(time_end))

            geo_dir_string = options.get("geo_dir", None)
            if geo_dir_string:
                geodirectory = strftime(
                    satscene.time_slot, geo_dir_string) % values
            else:
                geodirectory = directory
            logger.debug("Geodir = " + str(geodirectory))

            geofile_list = []
            geo_filenames_string = options.get("geo_filenames", None)
            if geo_filenames_string:
                geo_filenames_tmpl = strftime(satscene.time_slot,
                                              geo_filenames_string) % values
                geofile_list = glob.glob(os.path.join(geodirectory,
                                                      geo_filenames_tmpl))
                logger.debug("List of geo-files: " + str(geofile_list))
                # Only take the files in the interval given:
                geofile_list = _get_swathsegment(
                    geofile_list, time_start, time_end)

            logger.debug("List of geo-files (after time interval selection): "
                         + str(geofile_list))

        filenames = [os.path.basename(s) for s in file_list]

        glob_info = {}

        logger.debug("Channels to load: " + str(satscene.channels_to_load))
        for chn in satscene.channels_to_load:
            # Take only those files in the list matching the band:
            # (Filename starts with 'SV' and then the band-name)
            fnames_band = []

            try:
                fnames_band = [s for s in filenames if s.find('SV' + chn) >= 0]
            except TypeError:
                logger.warning('Band frequency not available from VIIRS!')
                logger.info('Asking for channel' + str(chn) + '!')

            if len(fnames_band) == 0:
                continue

            filename_band = [
                os.path.join(directory, fname) for fname in fnames_band]
            logger.debug("fnames_band = " + str(filename_band))

            band = ViirsBandData(filename_band, calibrate=calibrate).read()
            logger.debug('Band id = ' + band.band_id)

            # If the list of geo-files is not specified in the config file or
            # some of them do not exist, we rely on what is written in the
            # band-data metadata header:
            if len(geofile_list) < len(filename_band):
                geofilenames_band = [os.path.join(geodirectory, gfile) for
                                     gfile in band.geo_filenames]
                logger.debug("Geolocation filenames for band: " +
                             str(geofilenames_band))
                # Check if the geo-filenames found from the metadata actually
                # exist and issue a warning if they do not:
                for geofilename in geofilenames_band:
                    if not os.path.exists(geofilename):
                        logger.warning("Geo file defined in metadata header " +
                                       "does not exist: " + str(geofilename))

            elif band.band_id.startswith('M'):
                geofilenames_band = [geofile for geofile in geofile_list
                                     if os.path.basename(geofile).startswith('GMTCO')]
                if len(geofilenames_band) != len(filename_band):
                    # Try the geoid instead:
                    geofilenames_band = [geofile for geofile in geofile_list
                                         if os.path.basename(geofile).startswith('GMODO')]
                    if len(geofilenames_band) != len(filename_band):
                        raise IOError("Not all geo location files " +
                                      "for this scene are present for band " +
                                      band.band_id + "!")
            elif band.band_id.startswith('I'):
                geofilenames_band = [geofile for geofile in geofile_list
                                     if os.path.basename(geofile).startswith('GITCO')]
                if len(geofilenames_band) != len(filename_band):
                    # Try the geoid instead:
                    geofilenames_band = [geofile for geofile in geofile_list
                                         if os.path.basename(geofile).startswith('GIMGO')]
                    if len(geofilenames_band) != len(filename_band):
                        raise IOError("Not all geo location files " +
                                      "for this scene are present for band " +
                                      band.band_id + "!")
            elif band.band_id.startswith('D'):
                geofilenames_band = [geofile for geofile in geofile_list
                                     if os.path.basename(geofile).startswith('GDNBO')]
                if len(geofilenames_band) != len(filename_band):
                    raise IOError("Not all geo-location files " +
                                  "for this scene are present for " +
                                  "the Day Night Band!")

            band.read_lonlat(geofilepaths=geofilenames_band)

            if not band.band_desc:
                logger.warning('Band name = ' + band.band_id)
                raise AttributeError('Band description not supported!')

            satscene[chn].data = band.data
            satscene[chn].info['units'] = band.units
            satscene[chn].info['band_id'] = band.band_id
            satscene[chn].info['start_time'] = band.begin_time
            satscene[chn].info['end_time'] = band.end_time

            # We assume the same geolocation should apply to all M-bands!
            # ...and the same to all I-bands:

            from pyresample import geometry

            satscene[chn].area = geometry.SwathDefinition(
                lons=np.ma.masked_where(band.data.mask,
                                        band.geolocation.longitudes,
                                        copy=False),
                lats=np.ma.masked_where(band.data.mask,
                                        band.geolocation.latitudes,
                                        copy=False))
            area_name = ("swath_" + satscene.fullname + "_" +
                         str(satscene.time_slot) + "_"
                         + str(satscene[chn].data.shape) + "_" +
                         band.band_uid)
            satscene[chn].area.area_id = area_name
            satscene[chn].area_id = area_name
            # except ImportError:
            #    satscene[chn].area = None
            #    satscene[chn].lat = np.ma.array(band.latitude, mask=band.data.mask)
            #    satscene[chn].lon = np.ma.array(band.longitude, mask=band.data.mask)

            # if 'institution' not in glob_info:
            ##    glob_info['institution'] = band.global_info['N_Dataset_Source']
            # if 'mission_name' not in glob_info:
            ##    glob_info['mission_name'] = band.global_info['Mission_Name']

        ViirsGeolocationData.clear_cache()

        # Compulsory global attribudes
        satscene.info["title"] = (satscene.satname.capitalize() +
                                  " satellite, " +
                                  satscene.instrument_name.capitalize() +
                                  " instrument.")
        if 'institution' in glob_info:
            satscene.info["institution"] = glob_info['institution']

        if 'mission_name' in glob_info:
            satscene.add_to_history(glob_info['mission_name'] +
                                    " VIIRS SDR read by mpop")
        else:
            satscene.add_to_history("NPP/JPSS VIIRS SDR read by mpop")

        satscene.info["references"] = "No reference."
        satscene.info["comments"] = "No comment."

        satscene.info["start_time"] = min([chn.info["start_time"]
                                           for chn in satscene
                                           if chn.is_loaded()])
        satscene.info["end_time"] = max([chn.info["end_time"]
                                         for chn in satscene
                                         if chn.is_loaded()])


def get_lonlat(filename):
    """Read lon,lat from hdf5 file"""
    logger.debug("Geo File = " + filename)

    md = HDF5MetaData(filename).read()

    lats, lons = None, None
    h5f = h5py.File(filename, 'r')
    for key in md.get_data_keys():
        if key.endswith("Latitude"):
            lats = h5f[key].value
        if key.endswith("Longitude"):
            lons = h5f[key].value
    h5f.close()

    return (np.ma.masked_less(lons, -999, False),
            np.ma.masked_less(lats, -999, False))


def get_lonlat_into(filename, out_lons, out_lats, out_mask):
    """Read lon,lat from hdf5 file"""
    logger.debug("Geo File = " + filename)

    md = HDF5MetaData(filename).read()

    h5f = h5py.File(filename, 'r')
    for key in md.get_data_keys():
        if key.endswith("Latitude"):
            h5f[key].read_direct(out_lats)
            out_mask = out_lats < -999
        if key.endswith("Longitude"):
            h5f[key].read_direct(out_lons)
    h5f.close()


def globify(filename):
    filename = filename.replace("%Y", "????")
    filename = filename.replace("%m", "??")
    filename = filename.replace("%d", "??")
    filename = filename.replace("%H", "??")
    filename = filename.replace("%M", "??")
    filename = filename.replace("%S", "??")
    return filename


def _get_times_from_npp(filename):

    bname = os.path.basename(filename)
    sll = bname.split('_')
    start_time = datetime.strptime(sll[2] + sll[3][:-1],
                                   "d%Y%m%dt%H%M%S")
    end_time = datetime.strptime(sll[2] + sll[4][:-1],
                                 "d%Y%m%de%H%M%S")
    if end_time < start_time:
        end_time += timedelta(days=1)
    return start_time, end_time


def _get_swathsegment(filelist, time_start, time_end=None, area=None):
    """
    Return only the granule files for the time interval or area.
    """
    if area is not None:
        from trollsched.spherical import SphPolygon
        from trollsched.boundary import AreaBoundary

        lons, lats = area.get_boundary_lonlats()
        area_boundary = AreaBoundary((lons.side1, lats.side1),
                                     (lons.side2, lats.side2),
                                     (lons.side3, lats.side3),
                                     (lons.side4, lats.side4))
        area_boundary.decimate(500)
        contour_poly = area_boundary.contour_poly

    segment_files = []
    for filename in filelist:

        timetup = _get_times_from_npp(filename)

        # Search for multiple granules using an area
        if area is not None:
            md = NPPMetaData(filename)
            md.read()
            coords = np.vstack(md.get_ring_lonlats())
            poly = SphPolygon(np.deg2rad(coords))
            if poly.intersection(contour_poly) is not None:
                segment_files.append(filename)
            continue

        # Search for single granule using time start
        if time_end is None:
            if time_start >= timetup[0] and time_start <= timetup[1]:
                segment_files.append(filename)
                continue

        # search for multiple granules
        else:
            # check that granule start time is inside interval
            if timetup[0] >= time_start and timetup[0] <= time_end:
                segment_files.append(filename)
                continue

            # check that granule end time is inside interval
            if timetup[1] >= time_start and timetup[1] <= time_end:
                segment_files.append(filename)
                continue

    segment_files.sort()
    return segment_files
