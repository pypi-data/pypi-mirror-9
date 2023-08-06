#!/usr/bin/python
# -*- encoding:utf-8 -*-

import os
import sys
from shutil import copy

from ddp import *



# get project path
project_path = inc.get_project_path()

# draw spectrum
x = spec.SPEC()

# if have second param, then it must be lengend location.
if len(sys.argv) == 2:
    try:
        x.legend_loc = int(sys.argv[1])
    except TypeError:
        print 'lengend location should be a number in range 1..4.'
x.save_spec()

# if there exits the path, then copy it into it.
if os.path.exists('/var/www/html/images'):
    spec_path = os.path.join(project_path, 'spectrum.png')
    copy(spec_path, '/var/www/html/images')


