# -*- encoding:utf-8 -*-
# license: BSD style

from setuptools import setup, find_packages

setup(
    name='ddp',
    version='0.1',
    packages=find_packages(),
    package_data={
        'ddp': ['Template/*.tpl']
    },
    install_requires=['numpy', 'images2gif', 'matplotlib', 'PIL'],
    author='Xing',
    author_email='1281961491@qq.com',
    url='https://github.com/xingtingyang/ddp',
    license='BSD style',
    description='This is a package can be used to process vtr files.'
)
