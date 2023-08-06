# -*- encoding:utf-8 -*-

import ddp.inc as inc
import os


def get_ddpostprocess():
    tpl_path = inc.get_tpl_path('ddpostprocess')
    tpl_content = open(tpl_path, 'r').read()
    par_path = os.path.join(inc.get_project_path(), 'ddpostprocess.par')
    open(par_path, 'w').write(tpl_content)
    print 'ddpostprocess.par write successfully...'


def get_ddscat_fromfile():
    tpl_path =inc.get_tpl_path('ddscat_fromfile')
    tpl_content = open(tpl_path, 'r').read()
    par_path = os.path.join(inc.get_project_path(), 'ddscat.par')
    open(par_path, 'w').write(tpl_content)
    print 'ddscat.par from file write successfully...'


def get_ddscat_builtin():
    tpl_path =inc.get_tpl_path('ddscat_builtin')
    tpl_content = open(tpl_path, 'r').read()
    par_path = os.path.join(inc.get_project_path(), 'ddscat.par')
    open(par_path, 'w').write(tpl_content)
    print 'ddscat.par builtin write successfully...'