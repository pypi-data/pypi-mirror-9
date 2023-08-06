# -*- encoding:utf-8 -*-
# license: BSD style

from setuptools import setup, find_packages
import sys


# determin the include_scripts
include_scripts = []
if sys.platform == "win32":
    include_scripts = ['bin/ddp_getpar.py', 'bin/ddp_pvtr.py', 'bin/ddp_spec.py',
                       'bin/ddp_getpar.cmd', 'bin/ddp_pvtr.cmd', 'bin/ddp_spec.cmd']
else:
    include_scripts = ['bin/ddp_getpar.py', 'bin/ddp_pvtr.py', 'bin/ddp_spec.py']

# setup
setup(
    name='ddp',
    version='0.15',
    packages=find_packages(),
    package_data={
        'ddp': ['Template/*.tpl']
    },
    install_requires=['numpy', 'images2gif', 'matplotlib', 'PIL'],
    scripts=include_scripts,
    author='Xing',
    author_email='1281961491@qq.com',
    url='https://github.com/xingtingyang/ddp',
    license='BSD style',
    description='This is a package can be used to process vtr files.',
    long_description = open('README.md').read()
)
