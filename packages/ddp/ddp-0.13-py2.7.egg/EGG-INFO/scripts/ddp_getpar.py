#!d:\program files\enthought\canopy\user\scripts\python.exe
# -*- encoding:utf-8 -*-

import sys
from ddp import *


if len(sys.argv) == 2:
    if sys.argv[1] == '1':
        getpar.get_ddscat_fromfile()
    if sys.argv[1] == '2':
        getpar.get_ddscat_builtin()
    if sys.argv[1] == '3':
        getpar.get_ddpostprocess()
else:
    getpar.get_ddscat_fromfile()

