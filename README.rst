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

    $ pip install -r requirements.txt
    $ pip install -e .


Dependencies
============

* *Python* 3.3+ (no Python 2 support!)
* *Aaargh* for the command line tool
* *UltraJSON* (*ujson*) for fast JSON encoding and decoding (optional)
