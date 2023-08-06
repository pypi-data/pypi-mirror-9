#!/usr/bin/env python

"""Copy number variation toolkit: Infer copy number from targeted DNA sequencing."""

from os.path import dirname
from glob import glob

setup_args = {}

try:
    from setuptools import setup
    # Dependencies for easy_install and pip:
    setup_args.update(
        install_requires=[
            'numpy >= 1.6',
            'matplotlib >= 1.1',
            'pysam >= 0.8',
            'reportlab >= 3.0',
            'biopython >= 1.62',
        ])
except ImportError:
    from distutils.core import setup


DIR = (dirname(__file__) or '.') + '/'

setup_args.update(
    name='CNVkit',
    version='0.4.0',
    description=__doc__,
    author='Eric Talevich',
    author_email='eric.talevich@ucsf.edu',
    url='http://github.com/etal/cnvkit',
    packages=['cnvlib', 'cnvlib.ngfrills', 'cnvlib.segmentation'],
    scripts=[DIR + 'cnvkit.py'] + glob(DIR + 'scripts/*.py'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Healthcare Industry",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
)

setup(**setup_args)
