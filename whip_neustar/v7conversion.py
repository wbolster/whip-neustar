"""
Neustar (Quova) data set conversion module.

This module provides a routine to convert "old style" Quova data sets
into the Quova v7 format.
"""

import csv
import itertools

from . import reader

OLD_FORMAT_REF_HEADERS = frozenset(['carrier', 'org', 'sld', 'tld'])

OLD_FORMAT_FIELDS = (
    'start_ip_int',
    'end_ip_int',
    'cidr',
    'continent',
    'country',
    'country_iso2',
    'country_cf',
    'region',
    'state',
    'state_cf',
    'city',
    'city_cf',
    'postal_code',
    'phone_number_prefix',
    'timezone',
    'latitude',
    'longitude',
    'dma',
    'msa',
    'pmsa',
    'connectiontype',
    'linespeed',
    'ip_routingtype',
    'aol',
    'asn',
    'sld_id',
    'tld_id',
    'reg_org_id',
    'carrier_id',
)

OLD_FORMAT_NUMERICAL_FIELDS = [
    'asn',
    'city_cf',
    'country_cf',
    'dma',
    'msa',
    'phone_number_prefix',
    'postal_code',
    'state_cf',
]

OLD_FORMAT_RENAMED_FIELDS = {
    'connectiontype': 'connection_type',
    'country_iso2': 'country_code',
    'ip_routingtype': 'ip_routing_type',
    'linespeed': 'line_speed',
    'phone_number_prefix': 'area_code',
    'timezone': 'time_zone',
}

OLD_FORMAT_EMPTY_VALUES = frozenset(('', 'unknown', 'none'))


def clean_field_old_format(v):
    """Clean an input field (old data format)"""
    if v in OLD_FORMAT_EMPTY_VALUES:
        return None

    return v


def load_references(fp):
    references = {
        'carrier': {},
        'org': {},
        'sld': {},
        'tld': {},
    }
    ref_reader = csv.reader(fp, delimiter='|')
    for row in ref_reader:
        if not row[0] in OLD_FORMAT_REF_HEADERS:
            raise ValueError(
                "Unexpected input in reference data file: expected "
                "header line, got %r" % (row))

        ref_type, n_records, max_id = row
        for ref_id, value in itertools.islice(ref_reader, int(n_records)):
            references[ref_type][int(ref_id)] = clean_field_old_format(value)

    return references


def convert_to_v7(fp, references, out_fp):
    """Convert old format data and reference files to the V7 format"""

    # Prepare reader
    csv_reader = csv.DictReader(fp, OLD_FORMAT_FIELDS, delimiter='|')

    # Prepare writer
    writer = csv.DictWriter(
        out_fp, reader.FIELDS,
        delimiter=',',
        quoting=csv.QUOTE_ALL,
        quotechar='"',
        lineterminator='\n',
        extrasaction='ignore',
    )
    writer.writeheader()

    # Loop and transform
    n = 0
    for n, record in enumerate(csv_reader, 1):
        for k, v in record.iteritems():
            record[k] = clean_field_old_format(v)

        # Replace missing numerical values by empty strings
        for key in OLD_FORMAT_NUMERICAL_FIELDS:
            if record[key] == '0':
                record[key] = ''

        # Rename some fields
        for k1, k2 in OLD_FORMAT_RENAMED_FIELDS.iteritems():
            record[k2] = record.pop(k1)

        # Reference lookups
        record['carrier'] = references['carrier'][int(record['carrier_id'])]
        record['organization'] = references['org'][int(record['reg_org_id'])]
        record['sld'] = references['sld'][int(record['sld_id'])]
        record['tld'] = references['tld'][int(record['tld_id'])]

        # Drop magic "empty" value for time zones
        if record['time_zone'] == '999':
            record['time_zone'] = ''

        # Write output
        writer.writerow(record)

    return n
