# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='pyicane',
    version='0.1.2',
    author='Miguel Expósito Martín',
    author_email='miguel.exposito@gmail.com',
    packages=['pyicane', 'pyicane.test'],
    url='https://github.com/predicador37/pyicane',
    license='Apache License 2.0',
    description='Python wrapper for ICANE Statistical Data and Metadata API',
    long_description=open('README.rst').read(),
    install_requires=['pandas', 'requests'],
    test_suite='pyicane.test',
    keywords=['restful', 'json', 'statistics', 'dataframe', 'wrapper'],
    classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Scientific/Engineering :: Information Analysis',
          'Topic :: Software Development :: Libraries'
          ],
)
