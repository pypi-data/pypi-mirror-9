#from distutils.core import setup
from setuptools import setup

files = ['docs/*']

setup(
      name = 'west_map',
      version = '2.2',
      description = 'description',
      author = 'Sean West',
      url = 'tbd',
      packages = ['biomart', 'map'],
      package_data = {'package' : files},
      entry_points = {
                      'console_scripts':[
                                         'west_map = map.control:smain'
                                         ]
                      },
      scripts = ['run_map'],
      long_description = 'long description',
      classifiers = ['Programming Language :: Python', \
                     'Programming Language :: Python :: 3', \
                     'Operating System :: Unix', \
                     'Development Status :: 1 - Planning', \
                     'Intended Audience :: Science/Research', \
                     'Topic :: Scientific/Engineering :: Bio-Informatics', \
                     'Topic :: Scientific/Engineering :: Mathematics', \
                     'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', \
                     'Natural Language :: English']
      )