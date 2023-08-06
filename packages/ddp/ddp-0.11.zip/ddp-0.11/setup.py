# -*- encoding:utf-8 -*-
# license: BSD style

from setuptools import setup, find_packages

setup(
    name='ddp',
    version='0.11',
    packages=find_packages(),
    package_data={
        'ddp': ['Template/*.tpl']
    },
    install_requires=['numpy', 'images2gif', 'matplotlib', 'PIL'],
    scripts=['Bin/ddp_getpar.py', 'Bin/ddp_pvtr.py', 'Bin/ddp_spec.py'],
    author='Xing',
    author_email='1281961491@qq.com',
    url='https://github.com/xingtingyang/ddp',
    license='BSD style',
    description='This is a package can be used to process vtr files.',
    long_description = open('README.md').read()
)
