# -*- coding: utf-8 -*-"""

"""
setup packaging script for numerics python package
"""

import os

version = "0.0"
dependencies = ['numpy',
                'pandas',
                'matplotlib',
                'bokeh>=0.8.1',
                'python-dateutil',
                'which']

# allow use of setuptools/distribute or distutils
kw = {}
try:
    from setuptools import setup
    kw['entry_points'] = """
    [console_scripts]
    bar-chart = numerics.bar:main
    cat-columns = numerics.cat_columns:main
    display-fraction = numerics.text_display:main
    histogram = numerics.histogram:main
    interpolate = numerics.interpolation:main
    manipulate = numerics.manipulate:main
    mean = numerics.mean:main
    median = numerics.median:main
    plot = numerics.plot:main
    read-csv = numerics.read:main
    smooth = numerics.smooth:main
    sum = numerics.sum:main
    types = numerics.convert:main
"""
# TODO:
#   cleanse = numerics.clean:main  # cleans up outliers
#   fold = numerics.fold:main  # fold data through functions (reduce)
    kw['install_requires'] = dependencies
except ImportError:
    from distutils.core import setup
    kw['requires'] = dependencies

try:
    here = os.path.dirname(os.path.abspath(__file__))
    description = file(os.path.join(here, 'README.txt')).read()
except IOError:
    description = ''


setup(name='numerics',
      version=version,
      description="personal experiments in numerics + plotting",
      long_description=description,
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      author='Jeff Hammel',
      author_email='k0scist@gmail.com',
      url='http://k0s.org/hg/numerics',
      license='',
      packages=['numerics'],
      include_package_data=True,
      zip_safe=False,
      **kw
      )
