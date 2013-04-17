import logging
import os
import subprocess
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
# Have to do this after importing setuptools, which monkey patches distutils.
from distutils.extension import Extension

# Use Cython if available.
try:
    from Cython.Build import cythonize
except ImportError:
    cythonize = None

logging.basicConfig()
log = logging.getLogger()

# Parse the version from the fiona module.
with open('src/fiona/__init__.py', 'r') as f:
    for line in f:
        if line.find("__version__") >= 0:
            version = line.split("=")[1].strip()
            version = version.strip('"')
            version = version.strip("'")
            continue

# Get long description text from README.rst.
with open('README.rst', 'r') as f:
    readme = f.read()

with open('CREDITS.txt', 'r') as f:
    credits = f.read()

with open('CHANGES.txt', 'r') as f:
    changes = f.read()

# By default we'll try to get options via gdal-config. On systems without,
# options will need to be set in setup.cfg or on the setup command line.
include_dirs = []
library_dirs = []
libraries = []
try:
    gdal_config = "gdal-config"
    with open("gdal-config.txt", "w") as gcfg:
        subprocess.call([gdal_config, "--cflags"], stdout=gcfg)
        subprocess.call([gdal_config, "--libs"], stdout=gcfg)
    with open("gdal-config.txt", "r") as gcfg:
        cflags = gcfg.readline().strip()
        libs = gcfg.readline().strip()
    for item in cflags.split():
        if item.startswith("-I"):
            include_dirs.extend(item[2:].split(":"))
    for item in libs.split():
        if item.startswith("-L"):
            library_dirs.extend(item[2:].split(":"))
        elif item.startswith("-l"):
            libraries.append(item[2:])
except Exception as e:
    log.warning("Failed to get options via gdal-config: %s", str(e))

ext_options = dict(
    include_dirs=include_dirs,
    library_dirs=library_dirs,
    libraries=libraries)

# When building from a repo, Cython is required.
if os.path.exists("MANIFEST.in"):
    log.info("MANIFEST.in found, presume a repo, cythonizing...")
    if not cythonize:
        log.critical(
            "Cython.Build.cythonize not found. "
            "Cython is required to build from a repo.")
        sys.exit(1)
    ext_modules = cythonize([
        Extension('fiona.ogrinit', ['src/fiona/ogrinit.pyx'], **ext_options),
        Extension('fiona.ogrext', ['src/fiona/ogrext.pyx'], **ext_options)])
# If there's no manifest template, as in an sdist, we just specify .c files.
else:
    ext_modules = [
        Extension('fiona.ogrinit', ['src/fiona/ogrinit.c'], **ext_options),
        Extension('fiona.ogrext', ['src/fiona/ogrext.c'], **ext_options)]

setup(
    name='Fiona',
    version=version,
    description="Fiona reads and writes spatial data files",
    license='BSD',
    keywords='gis vector feature data',
    author='Sean Gillies',
    author_email='sean.gillies@gmail.com',
    maintainer='Sean Gillies',
    maintainer_email='sean.gillies@gmail.com',
    url='http://github.com/Toblerity/Fiona',
    long_description=readme + "\n" + changes + "\n" + credits,
    package_dir={'': 'src'},
    packages=['fiona'],
    install_requires=[],
    tests_require=['nose'],
    test_suite='nose.collector',
    ext_modules=ext_modules,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: GIS',
    ],
)
