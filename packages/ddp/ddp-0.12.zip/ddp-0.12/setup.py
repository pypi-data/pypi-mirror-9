# -*- encoding:utf-8 -*-
# license: BSD style

from setuptools import setup, find_packages

setup(
    name='ddp',
    version='0.12',
    packages=find_packages(),
    package_data={
        'ddp': ['Template/*.tpl']
    },
    install_requires=['numpy', 'images2gif', 'matplotlib', 'PIL'],
    scripts=['bin/ddp_getpar.py', 'bin/ddp_pvtr.py', 'bin/ddp_spec.py'],
    author='Xing',
    author_email='1281961491@qq.com',
    url='https://github.com/xingtingyang/ddp',
    license='BSD style',
    description='This is a package can be used to process vtr files.',
    long_description = open('README.md').read()
)
