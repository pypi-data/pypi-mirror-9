# coding: utf-8

import sys

from setuptools import setup


if sys.version_info < (3,3):
    sys.stdout.write("At least Python 3.3 is required.\n")
    sys.exit(1)


# load version info
exec(open("alpaca/version.py").read())


setup(
    name="alpaca-variant-caller",
    version=__version__,
    author="Johannes Köster",
    author_email="johannes.koester@tu-dortmund.de",
    description="An algebraic parallel SNV caller using OpenCL",
    license="MIT",
    url="https://alpaca.readthedocs.org",
    packages=["alpaca", "alpaca.index", "alpaca.caller", "alpaca.show"],
    zip_safe=False,
    install_requires=["pyopencl>=2013.2", "h5py", "numpy", "mako", "scipy"],
    entry_points={"console_scripts": ["alpaca = alpaca:main"]},
    package_data={'': ['*.html']},
    classifiers=[
        "Development Status :: 4 - Beta",
        #"Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Bio-Informatics"
    ]
)
