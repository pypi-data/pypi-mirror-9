#!/usr/bin/env python

from setuptools import setup

setup(name = 'metameta',
      version = '0.0.0.11',
      description = 'Toolset for analyzing'\
          + 'metatranscriptome data mapped onto metagenomic data',
      classifiers = [
            'Development Status :: 2 - Pre-Alpha',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3.4',
            'Topic :: Scientific/Engineering :: Bio-Informatics'
          ],
      keywords = 'bioinformatics metadata metagenome metatranscriptome'\
          + 'short reads mapping alignment',
      url = 'https://github.com/Brazelton-Lab/metameta',
      download_url = 'https://github.com/Brazelton-Lab/metameta/tarball/'\
          + '0.0.0.11',
      author = 'Alex Hyer',
      author_email = 'theonehyer@gmail.com',
      license = 'GPL',
      packages = ['metameta'],
      include_package_data = True,
      zip_safe = False,
      test_suite = 'nose.collector',
      tests_require = ['nose'],
      install_requires = [
          'pysam'
          ],
      entry_points = {
        'console_scripts':['metameta = metameta.__main__:main']
        },
      )
