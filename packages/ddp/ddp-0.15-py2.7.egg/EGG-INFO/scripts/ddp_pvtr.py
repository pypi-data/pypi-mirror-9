#!d:\program files\enthought\canopy\user\scripts\python.exe
# -*- encoding:utf-8 -*-

import sys
from ddp import *


pvtr = pvtr.PVTR()

if len(sys.argv) == 3:
    # if there exits three params
    if sys.argv[1] == "gos":
        pvtr.get_origin_slice(sys.argv[2])
    if sys.argv[1] == "gas":
        pvtr.get_all_slice(sys.argv[2])
    if sys.argv[1] == "sos":
        pvtr.set_origin_slice(sys.argv[2])
    if sys.argv[1] == "sas":
        pvtr.set_all_slice(sys.argv[2])
else:
    # default options
    pvtr.get_origin_slice('x_slice')
