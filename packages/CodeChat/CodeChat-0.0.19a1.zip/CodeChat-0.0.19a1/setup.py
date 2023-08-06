# .. -*- coding: utf-8 -*-
#
#    Copyright (C) 2012-2015 Bryan A. Jones.
#
#    This file is part of CodeChat.
#
#    CodeChat is free software: you can redistribute it and/or modify it under
#    the terms of the GNU General Public License as published by the Free
#    Software Foundation, either version 3 of the License, or (at your option)
#    any later version.
#
#    CodeChat is distributed in the hope that it will be useful, but WITHOUT ANY
#    WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#    FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#    details.
#
#    You should have received a copy of the GNU General Public License along
#    with CodeChat.  If not, see <http://www.gnu.org/licenses/>.
#
# ***************************************
# setup.py - Package and install CodeChat
# ***************************************
# Builds and installs CodeChat.
#
# Packaging notes
# ===============
# Packaging on Python is a mess, IMHO. It takes an easy job and makes it hard.
#
# A quick summary: distutils_ can't
# install dependencies from PyPi_, so use setuptools_. A source distribution is
# a good idea becaues it can run on a bare Python installation with no other
# installs required, but there's no standard format (.zip?, .tar.gz?, etc.). An
# .egg is nice, but requires setuptools/pip/ez_setup installed. The .whl
# (`Python wheel <http://wheel.readthedocs.org/en/latest/>`_)
# is the latest and greatest format that superceeds eggs, but with similar
# problems (requires wheel to be installed).
#
# Reading to get up to speed:
#
# * `Python Packaging User Guide <http://packaging.python.org/en/latest/>`_ -
#   the most up-to-date reference I've found so far. Tells which tools to
#   actually use. It was `forked <http://packaging.python.org/en/latest/history.html#id2>`__
#   from `The Hitchhiker's Guide to Packaging <http://guide.python-distribute.org/>`_,
#   which is outdated, unfortunately, but used to be helpful.
#
# * `How To Package Your Python Code <http://www.scotttorborg.com/python-packaging/index.html>`_:
#   A useful tutorial on what to do. Doesn't cover eggs/wheels, though.
#
# * `distutils <http://docs.python.org/distutils/index.html>`_ - The built-in
#   installer. Tells what to do, but not what actually happens. It doesn't have
#   the ability to install dependencies from `PyPi <http://pypi.python.org>`_,
#   which I need.
#
# * `setuptools <https://pythonhosted.org/setuptools>`_ - A distutils
#   replacement which can install dependencies, so I use it.
#
# Questions / to do
# =================
# * Add a `setup.cfg <https://docs.python.org/2/distutils/configfile.html>`_
#   with defaults.
#
# To package
# ==========
# Create a source distribution, a built distribution, then upload both:
#
#   ``python setup.py sdist bdist_wheel upload``
#
# To `upload docs <http://pythonhosted.org/setuptools/setuptools.html#upload-docs-upload-package-documentation-to-pypi>`_,
# which are placed `here <http://pythonhosted.org/CodeChat/>`__
# (make sure to run Sphinx first, so the docs will be current):
#
#    ``python setup.py upload_docs --upload-dir=_build\html``
#
# For `development <https://pythonhosted.org/setuptools/setuptools.html#development-mode>`_:
#
#  ``python setup.py develop``
#
# Yajo has `packaged this for Linux <https://build.opensuse.org/package/show/home:yajo:enki/python-codechat>`_.
# Thanks so much.
#
# Packaging script
# ================
# Otherwise known as the evils of ``setup.py``.
#
# For users who install this from source but don't have setuptools installed,
# `auto-install it <https://pythonhosted.org/setuptools/setuptools.html#using-setuptools-without-bundling-it>`__. When packing for Linux, downloads are blocked so we must specify
# a very old already-installed `version <http://pythonhosted.org/setuptools/history.html>`_.
# Leave this as a `patch <https://build.opensuse.org/package/view_file/home:yajo:enki/python-codechat/python-codechat.offline_setuptools.patch?expand=1>`_
# so that we normally uses a more modern version.
import ez_setup
ez_setup.use_setuptools()

# For version number.
import CodeChat

# PyPA copied code
# ----------------
# From `PyPA's sample setup.py <https://github.com/pypa/sampleproject/blob/master/setup.py>`__,
# read ``long_description`` from a file. This code was last updated on
# 21-Feb-2015 based on `this head <https://github.com/pypa/sampleproject/commit/3df8e577d7926051c364af1c8772c7ff3f97a396>`_.
from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# My code
# -------
setup(
    # This must comply with `PEP 0426 <http://legacy.python.org/dev/peps/pep-0426/#name>`_'s
    # name requirements.
    name='CodeChat',

    # Projects should comply with the `version scheme <http://legacy.python.org/dev/peps/pep-0440/#public-version-identifiers>`_
    # specified in PEP440. I use this so that my Sphinx  docs will have the same
    # version number. There are a lot of alternatives in `Single-sourcing the
    # Project Version <https://packaging.python.org/en/latest/single_source_version.html>`_.
    # I picked this because it seems simple and matches my Sphinx code.
    version=CodeChat.__version__,

    description="The CodeChat system for software documentation",
    long_description=long_description,

    # The project's main homepage.
    url='https://bitbucket.org/bjones/documentation/overview',

    # Obscure my e-mail address to help defeat spam-bots.
    author="Bryan A. Jones",
    author_email="bjones AT ece.msstate.edu",

    license='GPLv3+',

    # These are taken from the `full list <https://pypi.python.org/pypi?%3Aaction=list_classifiers>`_.
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Documentation',
        'Topic :: Text Processing :: Markup',
    ],

    keywords='literate programming',

    packages = ['CodeChat'],

    # This will be installed by pip when this project is installed. For more on
    # using “install_requires” see `install_requires vs Requirements files <https://packaging.python.org/en/latest/requirements.html>`_.
    install_requires=['docutils>=0.12'],

    # To package data files, I'm using ``include_package_data = True`` then
    # putting the files in ``MANIFEST.in``. See `including data files <http://pythonhosted.org/setuptools/setuptools.html#including-data-files>`_.
    include_package_data = True,
)
