"""
Command line interface module.
"""

import logging
import sys

import aaargh

JSON_LIBS = ('ujson', 'simplejson', 'json')

for lib in JSON_LIBS:
    try:
        json = __import__(lib)
    except ImportError:
        pass
    else:
        break

from .reader import iter_records

app = aaargh.App(
    description="Neustar (formerly Quova) data set utilities.")


@app.cmd(description="Convert a Neustar V7 dataset to Whip format")
@app.cmd_arg('filename')
def convert(filename):
    out_fp = sys.stdout

    write = out_fp.write
    dumps = json.dumps
    for doc in iter_records(filename):
        write(dumps(doc))
        write('\n')


def main():
    logging.basicConfig(
        format='%(asctime)s (%(name)s) %(levelname)s: %(message)s',
        level=logging.INFO,
    )
    app.run()


if __name__ == '__main__':
    main()
