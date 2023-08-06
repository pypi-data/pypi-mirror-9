# PlanetFilter

PlanetFilter uses a blacklist to filter a blog aggregator feed. It allows
anyone to subscribe to popular blog aggregators without being overwhelmed by
the noise.

It supports the RSS, RSS 2.0 and Atom formats.

## Installation

To install using pip, simply do this:

    $ pip install planetfilter

## Usage

To filter a given author out of a blog aggregator, create a config file for
that aggregator:

    [feed]
    url=http://planet.mozilla.org/rss20.xml

    [blacklist]
    authors = The Mozilla Blog
      Mozilla Release Management Team
    titles =
      Product Coordination Meeting

and then run:

    planetfilter --output filtered.xml planet.conf

Then in your feed reader, add the feed either using a `file:///` URL or
as an `http://localhost/` URL if you serve it using a local web server.

## Compatibility

PlanetFilter is known to work with the following feed readers:

* [Akregator](https://userbase.kde.org/Akregator) using `file:///` URLs
* [Thunderbird](https://www.mozilla.org/thunderbird/) using `http://localhost/` URLs

## License

Copyright (C) 2010, 2015  Francois Marier <francois@fmarier.org>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
