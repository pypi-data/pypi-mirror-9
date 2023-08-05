# -*- coding: utf-8 -*-

from setuptools import setup, Extension

setup(
    name='ip2cc_ng',
    description='Lookup country country by IP address',
    version='0.1',
    author='Viktor Kotseruba',
    author_email='barbuzaster@gmail.com',
    license='Python-style',
    keywords='web',
    url='https://github.com/barbuza/ip2cc_ng',
    zip_safe=False,
    ext_modules=[Extension('ip2cc', ['ip2cc.c', 'python_ext.c'])]
)
