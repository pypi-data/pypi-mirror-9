#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Thu 20 Sep 2012 14:43:19 CEST

"""Bindings for flandmark
"""

bob_packages = ['bob.core', 'bob.io.base']

from setuptools import setup, find_packages, dist
dist.Distribution(dict(setup_requires=['bob.extension', 'bob.blitz'] + bob_packages))
from bob.blitz.extension import Extension, build_ext

from bob.extension.utils import load_requirements
build_requires = load_requirements()

# Define package version
version = open("version.txt").read().rstrip()

packages = ['boost']
boost_modules = ['system']

# check if opencv is available
try:
  from bob.extension import check_packages
  pkg = check_packages(['opencv>=2.0'])
  print("Found OpenCV libraries %s" % pkg[0].libraries())
  packages.append('opencv>=2.0')
except RuntimeError as e:
  print("OpenCV was not found, it will not be availabe during tests")

setup(

    name="bob.ip.flandmark",
    version=version,
    description="Python bindings to the flandmark keypoint localization library",
    license="GPLv3",
    author='Andre Anjos',
    author_email='andre.anjos@idiap.ch',
    long_description=open('README.rst').read(),
    url='https://github.com/bioidiap/bob.ip.flandmark',

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    setup_requires = build_requires,
    install_requires = build_requires,

    namespace_packages=[
      "bob",
      "bob.ip",
    ],

    ext_modules=[
      Extension("bob.ip.flandmark.version",
        [
          "bob/ip/flandmark/version.cpp",
        ],
        bob_packages = bob_packages,
        version = version,
        packages = packages,
        boost_modules = boost_modules,
      ),

      Extension("bob.ip.flandmark._library",
        [
          "bob/ip/flandmark/flandmark_detector.cpp",
          "bob/ip/flandmark/liblbp.cpp",
          "bob/ip/flandmark/flandmark.cpp",
          "bob/ip/flandmark/main.cpp",
        ],
        bob_packages = bob_packages,
        version = version,
        packages = packages,
        boost_modules = boost_modules,
      ),
    ],

    cmdclass = {
      'build_ext': build_ext
    },

    classifiers = [
      'Framework :: Bob',
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],

)
