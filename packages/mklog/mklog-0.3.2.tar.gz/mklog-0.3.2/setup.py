#!/usr/bin/env python

"""Installer"""

from setuptools import setup, find_packages
import os

def readme():
    """Return content of file `./README.rst`."""
    directory = os.path.dirname(os.path.join(
        os.getcwd(),
        __file__,
        ))
    return open(os.path.join(directory, "README.rst"), "r").read()

setup(
    name='mklog',
    version="0.3.2",
    packages=find_packages(),
    setup_requires=["hgtools"],
    install_requires=[
        ],
    include_package_data=True,
    author='Louis Paternault',
    author_email='spalax@gresille.org',
    description='Append date and time before text',
    url='http://git.framasoft.org/spalax/mklog',
    license="GPLv3 or any later version",
    #test_suite="mklog.test.suite",
    entry_points={
        'console_scripts': ['mklog = mklog.main:main']
        },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Topic :: System :: Logging",
    ],
    long_description=readme(),
    zip_safe=True,
)
