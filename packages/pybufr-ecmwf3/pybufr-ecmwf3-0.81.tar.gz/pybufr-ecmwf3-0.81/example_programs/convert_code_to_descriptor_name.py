#!/usr/bin/env python3

'''a simple example script showing how to retrieve a description name
from a descroptor code.'''

# Copyright J. de Kloe
# This software is licensed under the terms of the LGPLv3 Licence
# which can be obtained from https://www.gnu.org/licenses/lgpl.html

from pybufr_ecmwf.bufr_table import BufrTable

BT = BufrTable()
BTABLE = 'pybufr_ecmwf/ecmwf_bufrtables/B2550000000098006001.TXT'
BT.load(BTABLE)

OBJ = BT.get_descr_object(int('001001', 10))
print('OBJ: ', OBJ)
print('OBJ.name: ', OBJ.name)
