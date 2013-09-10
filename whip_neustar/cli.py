"""
Command line interface module.
"""

import gzip
import logging
import sys

import aaargh

logger = logging.getLogger(__name__)

JSON_LIBS = ('ujson', 'simplejson', 'json')

for lib in JSON_LIBS:
    try:
        json = __import__(lib)
    except ImportError:
        pass
    else:
        break

from . import reader
from . import v7conversion


def gzip_wrap(fp):
    if fp.name.endswith('.gz'):
        return gzip.GzipFile(mode='r', fileobj=fp)
    else:
        return fp


app = aaargh.App(
    description="Neustar (formerly Quova) data set utilities.")


@app.cmd(description="Convert a Neustar V7 dataset to Whip format")
@app.cmd_arg('filename')
def convert(filename):
    out_fp = sys.stdout

    write = out_fp.write
    dumps = json.dumps
    for doc in reader.iter_records(filename):
        write(dumps(doc))
        write('\n')


@app.cmd(
    name='convert-to-v7',
    description="Convert an older Quova data set into V7 format")
@app.cmd_arg('data_fp', type=file, nargs='?', default=sys.stdin)
@app.cmd_arg('ref_fp', type=file, nargs='?')
@app.cmd_arg('--output', '-o', default=sys.stdout)
def convert_v7(data_fp, ref_fp, output):
    if ref_fp is None:
        logger.info("No reference file specified; trying to find it "
                    "based on data file name")
        if not '.dat' in data_fp.name:
            raise RuntimeError("Cannot deduce reference file name")
        ref_fp = open(data_fp.name.replace('.dat', '.ref'))

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
