#!/usr/bin/env python3

from os.path import dirname, exists, join
import sys, subprocess
from setuptools import setup
from urllib.request import urlretrieve

setup_dir = dirname(__file__)
base_package = 'hal_impl'
version_file = join(setup_dir, base_package, 'version.py')
hal_version = 'jenkins-stable-2015.312.beta'
hal_site = 'http://www.tortall.net/~robotpy/hal'
hal_file = join(setup_dir, base_package, 'libHALAthena_shared.so')

__version__ = "master"
__hal_version__ = None

# Read the version if it exists
if exists(version_file):
    with open(version_file, 'r') as fp:
        exec(fp.read(), globals())

# Download the HAL if required
if not exists(hal_file) or __hal_version__ != hal_version:
    print("Downloading libHALAthena_shared.so")
    def _reporthook(count, blocksize, totalsize):
        percent = int(count*blocksize*100/totalsize)
        sys.stdout.write("\r%02d%%" % percent)
        sys.stdout.flush()

    urlretrieve("%s/%s/libHALAthena_shared.so" % (hal_site, hal_version),
                hal_file, _reporthook)

# Automatically generate a version based on the git version
if exists(join(setup_dir, '..', '.git')):
    p = subprocess.Popen(["git", "describe", "--tags", "--dirty=-dirty"],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out, err = p.communicate()
    # Make sure the git version has at least one tag
    if err:
        print("Error: You need to create a tag for this repo to use the builder")
        sys.exit(1)

    version = out.decode('utf-8').rstrip()
else:
    version = __version__

# Generate a new version.py if required
if not exists(version_file) or __version__ != version or __hal_version__ != hal_version:
    with open(join(setup_dir, base_package, 'version.py'), 'w') as fp:
        fp.write("# Autogenerated by setup.py\n__version__ = '{0}'\n__hal_version__ = '{1}'".format(version, hal_version))


with open(join(setup_dir, 'README.rst'), 'r') as readme_file:
    long_description = readme_file.read()

setup(
    name='robotpy-hal-roborio',
    version=version,
    description='WPILib HAL layer for roboRIO platform',
    long_description=long_description,
    author='Peter Johnson, Dustin Spicuzza',
    author_email='robotpy@googlegroups.com',
    url='https://github.com/robotpy',
    keywords='frc first robotics hal can',
    packages=['hal_impl'],
    package_data={'hal_impl': ['libHALAthena_shared.so']},
    install_requires='robotpy-hal-base==' + version, # is this a bad idea?
    license="BSD License",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.4",
        "Topic :: Scientific/Engineering"
    ]
    )
