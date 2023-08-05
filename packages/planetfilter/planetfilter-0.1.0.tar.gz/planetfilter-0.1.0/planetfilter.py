#!/usr/bin/python3
#
# Planet Filter - feed filter for newsfeed aggregators
# Copyright (C) 2010, 2015  Francois Marier <francois@fmarier.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# http://docs.python.org/library/xml.dom.minidom.html
# http://docs.python.org/library/xml.dom.html
# http://docs.python.org/library/configparser.html

rdfns = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'

VERSION = '0.1.0'

import argparse
import configparser as cp
from urllib.request import urlopen
import xml.dom.minidom as minidom


def delete_node(node):
    parent = node.parentNode
    parent.removeChild(node)


def delete_rss1_item(item):
    # Delete refernce to the item
    rdfabout = item.getAttributeNS(rdfns, 'about')
    rdfnode = item.parentNode
    channel = rdfnode.getElementsByTagName('channel').item(0)
    rdfseq = channel.getElementsByTagNameNS(rdfns, 'Seq').item(0)
    rdflist = rdfseq.getElementsByTagNameNS(rdfns, 'li')
    for li in rdflist:
        if li.getAttributeNS(rdfns, 'resource') == rdfabout:
            delete_node(li)

    # Delete the item
    delete_node(item)


def is_rss2(xmldocument):
    rsslist = xmldocument.getElementsByTagName('rss')
    if rsslist.length != 1:
        return False
    else:
        # Check the version
        rss = rsslist.item(0)
        if rss.getAttribute('version') != '2.0':
            return False
        else:
            return True


def is_rss1(xmldocument):
    rdflist = xmldocument.getElementsByTagNameNS(rdfns, 'RDF')
    if rdflist.length != 1:
        return False
    else:
        # Check the namespace/version
        rdf = rdflist.item(0)
        if rdf.getAttribute('xmlns').find('purl.org/rss/1.0') > -1:
            return True
        else:
            return False


def is_atom(xmldocument):
    feedlist = xmldocument.getElementsByTagName('feed')
    if feedlist.length != 1:
        return False
    else:
        # Check the namespace/version
        feed = feedlist.item(0)
        if feed.getAttribute('xmlns').find('w3.org/2005/Atom') > -1:
            return True
        else:
            return False


def filter_rss2(xmldocument, blacklist):
    rss = xmldocument.getElementsByTagName('rss').item(0)
    channel = rss.getElementsByTagName('channel').item(0)
    items = channel.getElementsByTagName('item')
    for item in items:
        titles = item.getElementsByTagName('title')
        for title in titles:
            textnode = title.firstChild
            if minidom.Node.TEXT_NODE == textnode.nodeType:
                titlestring = textnode.nodeValue
                for author in blacklist:
                    if 0 == titlestring.find(author):
                        delete_node(item)
    return True


def filter_atom(xmldocument, blacklist):
    feed = xmldocument.getElementsByTagName('feed').item(0)
    entries = feed.getElementsByTagName('entry')
    for entry in entries:
        authors = entry.getElementsByTagName('author')
        for author in authors:
            name = author.getElementsByTagName('name').item(0)
            textnode = name.firstChild
            if minidom.Node.TEXT_NODE == textnode.nodeType:
                authorstring = textnode.nodeValue
                for author in blacklist:
                    if 0 == authorstring.find(author):
                        delete_node(entry)
    return True


def filter_rss1(xmldocument, blacklist):
    rdf = xmldocument.getElementsByTagNameNS(rdfns, 'RDF').item(0)
    items = rdf.getElementsByTagName('item')
    for item in items:
        titles = item.getElementsByTagName('title')
        for title in titles:
            textnode = title.firstChild
            if minidom.Node.TEXT_NODE == textnode.nodeType:
                titlestring = textnode.nodeValue
                for author in blacklist:
                    if 0 == titlestring.find(author):
                        delete_rss1_item(item)
    return True


def filter_feed(xmldocument, blacklist):
    if is_rss2(xmldocument):
        return filter_rss2(xmldocument, blacklist)
    elif is_rss1(xmldocument):
        return filter_rss1(xmldocument, blacklist)
    elif is_atom(xmldocument):
        return filter_atom(xmldocument, blacklist)
    else:
        print('Unsupported feed type')
        return False


def process_config(configfile, outfile):
    # TODO: check the return values for all of these
    config = cp.SafeConfigParser()
    config.read(configfile)
    url = config.get('feed', 'url')
    blacklist = config.get('blacklist', 'authors').split("\n")

    # TODO: check the return values for all of these
    fh = urlopen(url)
    contents = fh.read()
    document = minidom.parseString(contents)

    if blacklist and blacklist != ['']:
        filter_feed(document, blacklist)

    if outfile:
        # TODO: make sure we're not overwriting the file (unless --force)
        with open(outfile, 'w') as f:
            f.write(document.toxml())
    else:
        print(document.toxml())


def main():
    parser = argparse.ArgumentParser(
        description='Blacklist-based filter for blog aggregators.')
    parser.add_argument('configfile', type=str,
                        help='the config file to parse')
    parser.add_argument('-o', '--output', metavar='file',
                        required=False, type=str,
                        help='the output filename (default: <STDOUT>)')
    parser.add_argument('--version', action='version',
                        version='planetfilter %s' % VERSION)
    args = parser.parse_args()
    process_config(args.configfile, args.output)

main()
