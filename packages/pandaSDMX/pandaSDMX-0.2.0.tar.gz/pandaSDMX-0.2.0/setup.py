# encoding: utf-8

# pandaSDMX is licensed under the Apache 2.0 license a copy of which
# is included in the source distribution of pandaSDMX.
# This is notwithstanding any licenses of third-party software included in
# this distribution.
# (c) 2014, 2015 Dr. Leo <fhaxbox66qgmail.com>


# (c) 2014, 2015 Dr. Leo <fhaxbox66qgmail.com>


from setuptools import setup
from codecs import open


# Publish README on PYPI when uploading.
long_descr = open('description.rst', 'r').read()

setup(name='pandaSDMX',
      version='0.2.0',
      description='A Python- and pandas-powered client for Statistical Data and Metadata eXchange',
      long_description=long_descr,
      author='Dr. Leo',
      author_email='fhaxbox66@gmail.com',
      packages=['pandasdmx', 'pandasdmx.reader', 'pandasdmx.writer',
                'pandasdmx.utils', 'pandasdmx.tests'],
      package_data={
          'pandasdmx.tests': ['data/*/*.xml',
                              'data/EXR/*/*/*.xml', 'data/query/*.xml', 'data/common/*.xml']},
      url='https://github.com/dr-leo/pandasdmx',
      install_requires=[
          'pandas',
          'lxml',
          'requests'
      ],
      provides=['pandasdmx'],
      classifiers=[
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'Intended Audience :: Financial and Insurance Industry',
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Topic :: Scientific/Engineering',
          'Topic :: Scientific/Engineering :: Information Analysis'
      ]

      )
