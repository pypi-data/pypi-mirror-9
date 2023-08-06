#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 16 Apr 08:18:08 2012 CEST

from setuptools import setup, find_packages

# Define package version
version = open("version.txt").read().rstrip()

# The only thing we do in this file is to call the setup() function with all
# parameters that define our package.
setup(

    name='antispoofing.motion',
    version=version,
    description='Motion counter-measures for the REPLAY-ATTACK database',
    url='http://pypi.python.org/pypi/antispoofing.motion',
    license='GPLv3',
    author='Andre Anjos',
    author_email='andre.anjos@idiap.ch',
    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,

    namespace_packages=[
      "antispoofing",
      ],

    install_requires=[
      "setuptools",
      "bob.db.base",
      "bob.db.replay",
      "bob.db.casia_fasd",
      "antispoofing.utils",
    ],

    entry_points={

      'console_scripts': [
        'motion_framediff.py = antispoofing.motion.script.framediff:main',
        'motion_diffcluster.py = antispoofing.motion.script.diffcluster:main',
        'motion_rproptrain.py = antispoofing.motion.script.rproptrain:main',
        'motion_ldatrain.py = antispoofing.motion.script.ldatrain:main',
        'motion_time_analysis.py = antispoofing.motion.script.time_analysis:main',
        'motion_make_scores.py = antispoofing.motion.script.make_scores:main',
        'motion_merge_scores.py = antispoofing.motion.script.merge_scores:main',
        ],

      },

)
