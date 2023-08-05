#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Quick and dirty RSS to StatusNet client

Git repository: http://git.tenak.net/?p=rss2sn.git
"""
__version__ = "1.0.1"
__license__ = """
Copyright (C) 2015 marcos@tenak.net

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
__author__ = "marc0s <marcos+rss2sn@tenak.net>"

import argparse
import ConfigParser
import os

from argparse import RawDescriptionHelpFormatter
from datetime import datetime

from dateutil.parser import *
from dateutil.relativedelta import *
import feedparser
import statusnet

LAST = None

def get_last_item():
    """Reads tstamp_file and return its contents.

    Manage if the file does not exists.
    """
    # Handle missing tstamp file
    try:
        filep = open(TFILE, 'r')
    except IOError:
        filep = open(TFILE, 'w')
        # If BOOTSTRAP is set, store one year old date
        # This way we make (almost) sure that some content will
        # get posted
        since = datetime.now()
        if BOOTSTRAP:
            since = datetime.now() - relativedelta(years=1)
        filep.write(since.strftime(DATE_FORMAT))
        filep.close()
    finally:
        filep = open(TFILE, 'r')
        tstamp = filep.read()
        filep.close()
        tstamp = parse(tstamp, ignoretz=True)
    return tstamp

def post_notice(entry, since=None):
    """Send entry to SN instance if entry pub date > since
    """
    global LAST
    if (since and since < get_date(entry.published)) or not since:
        title = entry.title
        link = entry.link
        notice = "%s - %s #rss" % (title, link)
        notice = notice.encode('utf-8')
        SN.statuses_update(notice, source='rss2sn')
    if (LAST < get_date(entry.published)) or not since:
        LAST = get_date(entry.published)

def set_last_item(tstamp):
    """Saves the last entry timestamp
    """
    with open(TFILE, 'w') as filep:
        filep.write(tstamp.strftime(DATE_FORMAT))

def get_date(date_str):
    return parse(date_str, ignoretz=True)

def quickSort(arr):
    less = []
    pivotList = []
    more = []
    if len(arr) <= 1:
        return arr
    else:
        pivot = get_date(arr[0].published)
        for i in arr:
            if get_date(i.published) < pivot:
                less.append(i)
            elif get_date(i.published) > pivot:
                more.append(i)
            else:
                pivotList.append(i)
        less = quickSort(less)
        more = quickSort(more)
        return less + pivotList + more

if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=RawDescriptionHelpFormatter)
    PARSER.add_argument('--CONFIG', '-c', dest='CONFIG', type=str,
                        help='The CONFIGuration file')
    PARSER.add_argument('--account', '-a', dest='account', type=str,
                        required=True, help='The account to use')
    PARSER.add_argument('--version', '-v', action='version',
                        version='%(prog)s {version}'.format(version=__version__))
    ARGS = PARSER.parse_args()

    # The Config file contains one or more accounts like this:
    #
    # [AccountName]
    # site = http://my-status-net-instance.tld/api
    # username = alice
    # password = alicesecrets
    # feed = http://the-news-site-i-wanna-send-notices-from.tld/rss.xml
    # lastdir = ~/tmp
    #
    # And a Defaults SECTION with default values
    #
    # [Defaults]
    # lastdir = /tmp
    # dateformat = "%a, %d %b %Y %H:%M:%S"
    # validate_ssl = True
    # bootstrap = False
    #
    # dateformat is only used for *writing* the last item's timestamp,
    # input date format is guessed by python-dateutil.
    # Please note that Python2 does not support %z/%Z in date formatting!
    #

    CONFIG = ConfigParser.ConfigParser()
    CFGFILES = [os.path.expanduser('~/.rss2sn.cfg')]
    if ARGS.CONFIG:
        CFGFILES = [ARGS.CONFIG]
    if not CONFIG.read(CFGFILES):
        raise Exception("No configuration file found!")

    if not CONFIG.has_section(ARGS.account):
        raise Exception("The given account has no configuration available!")

    SECTION = ARGS.account
    try:
        LAST_DIR = CONFIG.get(SECTION, 'lastdir')
    except ConfigParser.NoOptionError:
        LAST_DIR = CONFIG.get('Defaults', 'lastdir')
    try:
        DATE_FORMAT = CONFIG.get(SECTION, 'dateformat')
    except ConfigParser.NoOptionError:
        DATE_FORMAT = CONFIG.get('Defaults', 'dateformat')
    try:
        BOOTSTRAP = CONFIG.getboolean(SECTION, 'bootstrap')
    except ConfigParser.NoOptionError:
        BOOTSTRAP = CONFIG.getboolean('Defaults', 'bootstrap')
    TFILE = os.path.join(os.path.expanduser(LAST_DIR),
                         'tstamp-%s' % (SECTION,))

    try:
        VALIDATE_SSL = CONFIG.getboolean(SECTION, 'validate_ssl')
    except ConfigParser.NoOptionError:
        VALIDATE_SSL = CONFIG.getboolean('Defaults', 'validate_ssl')


    SN = statusnet.StatusNet(CONFIG.get(SECTION, 'site'),
                             CONFIG.get(SECTION, 'username'),
                             CONFIG.get(SECTION, 'password'),
                             validate_ssl=VALIDATE_SSL)

    RSS = feedparser.parse(CONFIG.get(SECTION, 'feed'))
    LAST = get_last_item()
    # Sort RSS.entries, never assume the feed will be pubDate-ordered!
    entries = quickSort(RSS.entries)
    for rss_entry in entries:
        post_notice(rss_entry, since=LAST)
    set_last_item(LAST)
