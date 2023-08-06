# Copyright 2015 University of York
# Author: Aaron Ecay
# Released under the terms of the GNU General Public License version 3
# Please see the file LICENSE distributed with this source code for further
# information.


def pyccle_to_text(s):
    return " ".join(map(lambda x: x.split("\t")[0],
                        s.split("\n")))
