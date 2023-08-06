#!/usr/bin/python
#
# This file is part of the vecnet.emod package.
# For copyright and licensing information about this package, see the
# NOTICE.txt and LICENSE.txt files in its top-level directory; they are
# available at https://github.com/vecnet/vecnet.emod
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0.  If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.
import json
import struct
import datetime
import sys


KoppenType = {
    "Af":  1,
    "Am":  2,
    "As":  3,
    "Aw":  4,
    "Bsh": 5,
    "Bsk": 6,
    "Bwh": 7,
    "Bwk": 8,
    "Cfa": 9,
    "Cfb": 10,
    "Cfc": 11,
    "Csa": 12,
    "Csb": 13,
    "Csc": 14,
    "Cwa": 15,
    "Cwb": 16,
    "Cwc": 17,
    "Dfa": 18,
    "Dfb": 19,
    "Dfc": 20,
    "Dfd": 21,
    "Dsa": 22,
    "Dsb": 23,
    "Dsc": 24,
    "Dwa": 25,
    "Dwb": 26,
    "Dwc": 27,
    "Dwd": 28,
    "EF":  29,
    "ET":  30
}


def create_koppen_file(filename, koppen_type, list_of_nodeid):
    """ Generate EMOD Koppen weather file for specified list of nodes
    (same type will be used for all nodes).

    :param filename: name of the file to be produced
    :param koppen_type: Koppen zone code (String - "Aw", "Cwb", "EF etc)
    :param list_of_nodeid: List of node ids
    :return: Metadata dictionary for this Koppen climate file (also saved as filename.json)
    """
    node_offsets = ""
    offset = 0
    koppen_type_code = KoppenType[koppen_type]
    with open(filename, "w") as fp:
        for nodeid in list_of_nodeid:
            fp.write(struct.pack('i', koppen_type_code))
            if nodeid > 4294967295:
                raise TypeError("Node id number %x is wrong, max value 0xFFFFFFFF" % nodeid)
            node_offsets += "%08x%08x" % (nodeid, offset)
            offset += 4

    metadata = {
        "Metadata": {
            "DateCreated": "%s" % datetime.datetime.now(),
            "Tool": "vecnet.emod.koppen",
            "Author": "",
            "IdReference": "Gridded world grump2.5arcmin",
            "DataProvenance": "",
            "NodeCount": len(list_of_nodeid)
        },
        "ModeOffests": node_offsets
    }
    with open(filename + ".json", "w") as fp:
        fp.write(json.dumps(metadata, indent=4))
    return metadata


if __name__ == "__main__":
    koppen_file_name = sys.argv[1]
    print "Usage: python -m vecnet.emod.koppen koppen.dat Aw [1,2,3,4]"
    create_koppen_file(koppen_file_name, sys.argv[2], eval(sys.argv[3]))
    print "File %s has been generated successfully" % koppen_file_name