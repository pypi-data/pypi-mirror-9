from distutils.core import setup
import sys

setup(
    name = 'planetfilter',
    version = '0.1.0',
    description = 'Filter for blog aggregators',
    author = 'Francois Marier',
    author_email = 'francois@fmarier.org',
    url = 'https://launchpad.net/planetfilter',
    py_modules = ['planetfilter'],
    keywords = ['rss', 'atom', 'blogs', 'planet'],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        ],
    long_description = """\
PlanetFilter uses a blacklist to filter a blog aggregator feed. It
allows anyone to subscribe to popular blog aggregators without being
overwhelmed by the noise.

.. _project page: https://launchpad.net/planetfilter
"""
    )
