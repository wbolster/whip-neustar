Neustar utilities for Whip
==========================

This project provides a few utilities for Neustar (formerly Quova) data sets.
It is mostly intended to provide data set conversion so that the data can be
used by Whip.

Usage
=====

A CLI program named `whip-neustar-cli` provides the main functionality through
subcommands. Details::

    $ whip-neustart-cli --help


Installation
============

To install the package from a source tree::

    $ pip install -e .

To install from a source package:

    $ pip install whip_neustar   # or "whip_neustar_$VERSION.tar.gz"


Dependencies
============

* `aaargh` for the command line interface
* `ujson` for JSON encoding (optional, only for performance reasons)
