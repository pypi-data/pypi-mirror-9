#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2015 University of York
# Author: Aaron Ecay
# Released under the terms of the GNU General Public License version 3
# Please see the file LICENSE distributed with this source code for further
# information.

"""A search program for the PYCCLE-TCP corpus."""

from __future__ import print_function

# from wng import metadata
from wng import pattern, util

import click
import sys
import csv
import os

# TODO: code coverage


@click.command()
@click.option("--search-file", "-s", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.File("w"))
@click.argument("files", nargs=-1, type=click.Path(exists=True))
def main(search_file, files, output):
    """This program searches the PYCCLE corpus for a Part-of-Speech/text
    sequence.

    The argument SEARCH_FILE specifies the path to a search file; consult the
    program's documentation for the details of this format.  The remaining
    arguments are taken to be the path to files from the corpus, which will be
    searched.

    """
    if output is None:
        output = sys.stdout
    with open(search_file) as sf:
        search_text = sf.read()
        pat = pattern.parse_groups(search_text)
        captures = pattern.get_all_captures(search_text)
    writer = csv.DictWriter(output,
                            fieldnames=["file", "rule"] + captures +
                            ["match", "sentence"])
    writer.writeheader()
    for file in files:
        fname = os.path.basename(file).split(".")[0]
        with open(file) as f:
            sentences = f.read().split("\n\n")
            for sentence in sentences:
                for name, pat_rx in pat:
                    m = pat_rx.search(sentence)
                    if m:
                        gps = m.groupdict()
                        gps["file"] = fname
                        gps["sentence"] = util.pyccle_to_text(sentence)
                        gps["match"] = util.pyccle_to_text(m.group(0))
                        gps["rule"] = name
                        writer.writerow(gps)


def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv))


if __name__ == '__main__':
    main()
