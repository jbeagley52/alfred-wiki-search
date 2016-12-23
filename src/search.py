#!/usr/bin/env python
# encoding: utf-8
#
# GNU General Public License v3.0
#
#     Alfred Wiki Search - An Alfred Workflow for MediaWiki API searches
#     Copyright (C) 2016  Jonathan Beagley
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
# Created on 17 December 2016
#
from __future__ import unicode_literals, print_function

"""search.py [<query>]

Provide search results and URLs for <query> using Wikipedia's API
Alfred Wikipedia Search Module

Usage:

"""

import sys
import requests
import json
from pprint import pprint
from collections import OrderedDict
from workflow import Workflow3, ICON_WEB, ICON_WARNING

BASE_URL = 'https://en.wikipedia.org/'
API_URL = BASE_URL + 'w/api.php'
WEB_URL = BASE_URL + 'wiki/'
MOBILE_URL = 'https://en.m.wikipedia.org/wiki/'
HEADERS = {'user-agent': 'Alfred Wikipedia Search 0.0.1'}

log = None
"""Debug parameter
Possible values:
0 - no debug
1 - verbose
2 - very verbose
3 - dev only
"""
debug = 0

def normalize(title):
    return(title.replace(' ', '_'))

def get_page_url(title):
    title = normalize(title)
    page_url = WEB_URL + title
    if debug == 3:
        print(title)
    return(page_url)

def get_quicklook_url(title):
    title = normalize(title)
    quicklookurl = MOBILE_URL + title
    if debug == 3:
        print(title)
        print(quicklookurl)
    return(quicklookurl)

def get_thumbnail(image_url):
    thumb = requests.get(image_url)
    return(image_url)

def parse_results(results):
    """Parse Wikipedia (or potentially any MediaWiki) results into
    title, subtitle, etc.

    """
    items = []
    # Sort the results first using Wikipedia's index to get
    # our results in the same order as Wikipedia and stop Alfred
    # from doing it instead
    sorted_results = sorted(results.items(), key=lambda x: x[1]['index'])
    if debug == 3:
        pprint(sorted_results)
    for key, value in sorted_results:
        dct = dict()
        title = value['title']
        # Get the extract if it exists or else fail gracefully
        try:
            subtitle = value['extract']
        except:
            subtitle = ''
        # try to get the thumbnail url and somehow get Alfred to use it?
        try:
            image_url = get_thumbnail(value['thumbnail']['source'])
            icon = dict()
            icon['type'] = 'filetype'
            icon['path'] = image_url
            dct['icon'] = icon
        except:
            pass
        # Get mobile page URL for quick look
        quicklookurl = get_quicklook_url(value['title'])
        dct['quicklookurl'] = quicklookurl
        # Get normal web page URL for opening directly in default browser
        page_url = get_page_url(value['title'])
        dct['arg'] = page_url
        if debug == 2:
            print(index)
            print(title)
            print(subtitle)
        dct['title'] = title
        dct['subtitle'] = subtitle
        dct['largetext'] = subtitle
        dct['copytext'] = title
        dct['valid'] = True
        items.append(dct)
    if debug == 3:
        pprint(items)
    return(items)

def prepare_feedback(wf, items):
    """Prepare Alfred results of query.

    """
    if items != []:
        for item in items:
            wf.add_item(**item)
        wf.send_feedback()
    else:
        wf.add_item('Error!', 'No results found.',
                    icon=ICON_WARNING)
        wf.send_feedback()

def search(wf, query):
    """Search Wikipedia for `query`.

    """
    # Wikipedia search parameters
    search_params = {
        'action': 'query',
        'gsrsearch': query,
        'format': 'json',
        'prop': 'extracts',
        'generator': 'search',
        'gsrnamespace': '0',
        'gsrlimit': 10,
        'redirects': 1,
        'explaintext': '',
        'exsentences': 5,
        'exintro': 2,
        'exlimit': 'max',
        'excontinue': 1
    }

    # Request results in JSON
    r = requests.get(API_URL, params=search_params)
    r.raise_for_status()
    data = json.loads(r.content)
    if debug == 2:
        print(type(data))
        pprint(data)

    # Get only the results we want
    results = data['query']['pages']
    items = parse_results(results)
    if debug == 3:
        print(type(results))
        pprint(results)
        pprint(items)
    wf.cache_data('results', items)
    prepare_feedback(wf, items)

def main(wf):
    return(search(wf, wf.args[0]))

if __name__ == '__main__':
    wf = Workflow3()
    sys.exit(wf.run(main))
