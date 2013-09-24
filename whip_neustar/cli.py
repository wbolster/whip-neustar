"""
Command line interface module.
"""

import argparse
import datetime
import gzip
import io
import logging
import os
import re
import sys

import aaargh

logger = logging.getLogger(os.path.basename(sys.argv[0]))

for lib in ('ujson', 'simplejson', 'json'):
    try:
        json = __import__(lib)
        break
    except ImportError:
        pass

from . import reader
from . import v7conversion


def gzip_wrap(fp):
    if fp.name.endswith('.gz'):
        return gzip.open(fp, mode='rt', encoding='ascii')
    else:
        return io.TextIOWrapper(fp, encoding='ascii')


app = aaargh.App(
    description="Neustar (formerly Quova) data set utilities.")


@app.cmd(
    help="Convert a Neustar V7 dataset to Whip format")
@app.cmd_arg(
    'input',
    type=argparse.FileType('rb'),
    nargs='?',
    default=sys.stdin,
    help="Input data file (defaults to stdin)")
@app.cmd_arg(
    '--date',
    help="Date to use (YYYY-MM-DD)")
@app.cmd_arg(
    '--output', '-o',
    default=sys.stdout,
    help="Output file (defaults to stdout)")
def convert(input, date, output):
    if date is None:
        logger.info("No date specified; trying to extract from "
                    "file name")
        match = re.search(
            r'(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})\.csv',
            os.path.basename(input.name))
        if match is None:
            raise RuntimeError("Could not extract datetime from file name")
        match_dict = match.groupdict()
        year = int(match_dict['year'])
        month = int(match_dict['month'])
        day = int(match_dict['day'])
    else:
        year, month, day = map(int, date.split('-', maxsplit=2))

    fp = gzip_wrap(input)
    dt = datetime.datetime(year, month, day)
    logger.info("Converting input file %r using date %s", fp.name, dt)

    it = reader.iter_records(fp, dt)
    write = output.write
    dump = json.dump
    n = 0
    for n, doc in enumerate(it, 1):
        dump(doc, output)
        write('\n')

    logger.info("Converted %d records", n)


@app.cmd(
    name='convert-to-v7',
    help="Convert an older Quova data set into V7 format")
@app.cmd_arg(
    'data_fp',
    metavar="data-file",
    type=argparse.FileType('rb'),
    help="Input data file")
@app.cmd_arg(
    'ref_fp',
    metavar='references-file',
    type=argparse.FileType('rb'),
    nargs='?',
    help="Reference file name (optional, defauls to .ref file next to "
         "data file)")
@app.cmd_arg('--output', '-o', default=sys.stdout,
             help="Output file (defaults to stdout)")
def convert_v7(data_fp, ref_fp, output):
    if ref_fp is None:
        logger.info("No reference file specified; trying to find it "
                    "based on data file name")
        if not '.dat' in data_fp.name:
            raise RuntimeError("Cannot deduce reference file name")
        ref_fp = open(data_fp.name.replace('.dat', '.ref'), mode='rb')

    ref_fp = gzip_wrap(ref_fp)
    logger.info("Loading reference file %r into memory", ref_fp.name)
    references = v7conversion.load_references(ref_fp)

    logger.info("Converting input file %r", data_fp.name)
    data_fp = gzip_wrap(data_fp)

    n = v7conversion.convert_to_v7(data_fp, references, output)
    logger.info("Converted %d records", n)


def main():
    logging.basicConfig(
        format='%(asctime)s (%(name)s) %(levelname)s: %(message)s',
        level=logging.INFO,
    )
    app.run()


if __name__ == '__main__':
    main()
