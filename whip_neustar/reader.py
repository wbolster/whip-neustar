# encoding: UTF-8

"""
Neustar (Quova) data set reader module.
"""

import csv
import datetime
import itertools
import logging
import math
import os
import re
import socket
import struct

logger = logging.getLogger(__name__)

ISO8601_DATETIME_FMT = '%Y-%m-%dT%H:%M:%S'

# Regular expression to match file names. From the docs:
#
#    Data File V7 Naming Convention
#
#    Every file is named with information that qualifies the intended
#    recipient and data release information. The file name is named
#    using the following components:
#
#    <QuovaNet_customer_id>_v<data_version>_<internal_id>_<yyyymmdd>.csv.gz
#
#    For example, a file created from release version 470.63, production
#    job 15.27, on May 25, 2010 for customer quova would have the name:
#    quova_v470.63_15.27_20100525.gz
#
# However, in reality, the suffix is '.csv.gz', not '.gz'.
#
DATA_FILE_RE = re.compile(r'''
    ^
    (?P<customer_id>.+)
    _v(?P<version>.+)
    _(?P<internal_id>.+)
    _(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})
    \.csv(:?\.gz)?
    $
    ''', re.VERBOSE)

FIELDS = (
    'start_ip_int',
    'end_ip_int',
    'continent',
    'country',
    'country_code',
    'country_cf',
    'region',
    'state',
    'state_code',
    'state_cf',
    'city',
    'city_cf',
    'postal_code',
    'area_code',
    'time_zone',
    'latitude',
    'longitude',
    'dma',
    'msa',
    'connection_type',
    'line_speed',
    'ip_routing_type',
    'asn',
    'sld',
    'tld',
    'organization',
    'carrier',
    'anonymizer_status',
)
INTEGER_FIELDS = frozenset(('asn', 'country_cf', 'state_cf', 'city_cf'))
FLOAT_FIELDS = frozenset(('latitude', 'longitude'))
IGNORED_FIELDS = frozenset(('dma', 'msa'))


def clean_field(v):
    return None if v == '' else v


def format_ipv4_address(s, _inet_ntoa=socket.inet_ntoa,
                        _pack=struct.Struct('>L').pack):
    return _inet_ntoa(_pack(int(s)))


def iter_records(data_file):
    logger.info("Using data file %r", data_file)

    match = DATA_FILE_RE.match(os.path.basename(data_file))
    if not match:
        raise RuntimeError(
            "Unrecognized data file name: %r (is it the correct file?)"
            % data_file)

    match_dict = match.groupdict()
    version = match_dict['version']
    dt = datetime.datetime(int(match_dict['year']),
                           int(match_dict['month']),
                           int(match_dict['day']))
    dt_as_str = dt.strftime(ISO8601_DATETIME_FMT)

    logger.info(
        "Detected date %s and version %s for data file %r",
        dt_as_str, version, data_file)

    # Prepare for reading the CSV data
    with open(data_file, 'rb') as fp:
        reader = csv.reader(fp)
        it = iter(reader)

        # Skip header line, but make sure it is actually a header line
        header_line = next(it)
        if header_line[0] != FIELDS[0]:
            raise ValueError(
                "First line of input file %r does not seem a header line"
                % data_file)

        for n, record in enumerate(it, 1):

            out = dict(itertools.izip(FIELDS, map(clean_field, record)))

            # Data file information
            out['datetime'] = dt_as_str

            # Drop unwanted fields
            for k in IGNORED_FIELDS:
                del out[k]

            # Network information
            out['begin'] = format_ipv4_address(out.pop('start_ip_int'))
            out['end'] = format_ipv4_address(out.pop('end_ip_int'))

            # Convert numeric fields (if not None)
            for key in INTEGER_FIELDS:
                if out[key] is not None:
                    out[key] = int(out[key])
            for key in FLOAT_FIELDS:
                if out[key] is not None:
                    out[key] = float(out[key])

            # Convert time zone string like '-3.5' into ±HH:MM format
            if out['time_zone'] is not None:
                tz_frac, tz_int = math.modf(float(out['time_zone']))
                out['time_zone'] = '%+03d:%02d' % (tz_int, abs(60 * tz_frac))

            yield out

    logger.info("Finished reading %r (%d records)", data_file, n)