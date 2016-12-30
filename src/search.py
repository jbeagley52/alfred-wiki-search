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
from __future__ import unicode_literals

"""search.py [<query>]

Provide search results and URLs for <query> using Wikipedia's API
Alfred Wikipedia Search Module

Usage:

"""

import sys
import requests
import json
from collections import OrderedDict
from workflow import Workflow3, ICON_WEB, ICON_WARNING

HEADERS = {'user-agent': 'Alfred Wikipedia Search 1.0.0'}

log = None

def normalize(title):
    return(title.replace(' ', '_'))

def get_thumbnail(image_url):
    thumb = requests.get(image_url)
    return(image_url)

def fetch(url):
    # I want to prefetch pages for QuickLook
    page = requests.get(url)
    return(page)

def prepare_feedback(wf, items):
    """Prepare Alfred results of query.

    """
    if items != []:
        for item in items:
            wf.add_item(**item)
        wf.send_feedback()
        return(True)
    else:
        wf.add_item('Error!', 'No results found.',
                    icon=ICON_WARNING)
        wf.send_feedback()

class SearchEngine:

    _DEFAULT_ENGINE = {
                    'name': 'Wikipedia',
                    'url': 'https://en.wikipedia.org/'
                    }
    _SEARCH_PARAMS = {
                    'action': 'query',
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

    def __init__(self, engine=_DEFAULT_ENGINE,
                    params=_SEARCH_PARAMS, headers=HEADERS):
        self.name = engine['name']
        self.base_url = engine['url']
        self.api_url = self.base_url + 'w/api.php'
        self.web_url = self.base_url + 'wiki/'
        self.mobile_url = 'https://en.m.wikipedia.org/wiki/'
        self.search_params = params
        self.headers = headers

    def __call__(self, query):
        """Pass the query to engine after __init__"""
        # Update search_params with query
        self.search_params['gsrsearch'] = query
        # Request results in JSON
        r = requests.get(self.api_url,
                        params=self.search_params,
                        headers=self.headers)
        r.raise_for_status()
        data = json.loads(r.content)

        # Get only the results we want
        results = data['query']['pages']
        items = self.parse_results(results)
        return(items)

    def set_engine(self, engine):
        """Set the search engine to something other than default."""
        self.name = engine['name']
        # All of these are just examples for the time being
        self.api_url = 'http://www.physio-pedia.com/api.php'
        self.web_url = 'http://www.physio-pedia.com/'
        self.mobile_url = None
        return(True)

    def set_parameters(self, search_params):
        self.search_params = search_params
        return(True)

    def get_page_url(self, title):
        self.page_url = self.web_url + normalize(title)
        return(self.page_url)

    def get_quicklook_url(self, title):
        if self.mobile_url:
            self.quicklookurl = self.mobile_url + normalize(title)
        else:
            self.quicklookurl = self.get_page_url(title)
        return(self.quicklookurl)

    def parse_results(self, results):
        """Parse Wikipedia (or potentially any MediaWiki) results."""
        items = []
        # Sort the results first using Wikipedia's index to get
        # our results in the same order as Wikipedia and stop Alfred
        # from doing it instead
        sorted_results = sorted(results.items(), key=lambda x: x[1]['index'])
        for key, value in sorted_results:
            dct = dict()
            title = value['title']
            # Get the extract if it exists or else fail gracefully
            try:
                subtitle = value['extract']
            except KeyError:
                subtitle = ''
            # try to get the thumbnail url and somehow get Alfred to use it?
            #try:
                #image_url = get_thumbnail(value['thumbnail']['source'])
                #icon = dict()
                #icon['type'] = 'filetype'
                #icon['path'] = image_url
                #dct['icon'] = icon
            #except:
            #    pass
            # Get mobile page URL for quick look
            quicklookurl = self.get_quicklook_url(title)
            dct['quicklookurl'] = quicklookurl
            # Get normal web page URL for opening directly in default browser
            page_url = self.get_page_url(title)
            dct['arg'] = page_url
            dct['title'] = title
            dct['autocomplete'] = title
            dct['subtitle'] = subtitle
            dct['largetext'] = subtitle
            dct['copytext'] = title
            dct['valid'] = True
            items.append(dct)
        return(items)

def main(wf):
    # This is where I will introduce some logic in order to determine
    # which search engine is being used and/or let users set the engine

    # Somehow I want to be able to use a list of user-defined
    # config values for this - probably JSON/text format which enables
    # users to add their own search engines via the more user-friendly
    # Alfred interface
    query = wf.args[0]
    # Create instance of search class and pass query
    # Optional args: engine
    search = SearchEngine()
    # Fetch results
    items = search(query)
    # Cache results for later
    wf.cache_data('results', items)
    # Prepare and send feedback to Alfred
    prepare_feedback(wf, items)

if __name__ == '__main__':
    wf = Workflow3()
    sys.exit(wf.run(main))
