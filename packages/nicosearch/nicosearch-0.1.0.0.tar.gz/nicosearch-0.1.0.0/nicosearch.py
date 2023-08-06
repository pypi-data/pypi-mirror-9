#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import codecs
sys.stdout = codecs.getwriter('utf_8')(sys.stdout)
sys.stdin  = codecs.getreader('utf_8')(sys.stdin)

class SearchQueryBuilder(object):
    def __init__(self, keyword, **option):
        self._query = {
            'query'   :keyword,
            'service' : ['video'],
            'search'  : ['title'],
            'join'    : ['cmsid', 'title', 'view_counter'],
            'from'    : 0,
            'size'    : 10,
            'sort_by' : 'view_counter',
            'issuer'  : 'nicosearcy.py',
            'reason'  : 'searching niconico with python'
            }
        for k,v in option.items():
            if k is 'frm':
                k = 'from'
            self._query[k] = v

    def build(self):
        return self._query

class SearchRequest(object):
    URL = 'http://api.search.nicovideo.jp/api/'
    HEADERS = {'content-type': 'application/json'}

    def __init__(self, data, url=URL):
        self._data = data
        self._url = url

    def fetch(self):
        import requests, json
        return SearchResponse(requests.post(self._url, data=json.dumps(self._data), headers=self.HEADERS))

class SearchResponse(object):
    def __init__(self, response):
        self._response = response
        self._contents = self._filter_contents(self._response.text)

    @property
    def contents(self):
        return self._contents

    def _filter_contents(self, text):
        import json
        json_list = text.splitlines()

        json_object_list = []
        for json_object in json_list:
            json_object_list += [json.loads(json_object, 'utf-8')]

        contents = []
        for json_object in json_object_list:
            if 'values' in json_object.keys():
                for value in json_object['values']:
                    if 'cmsid' in value.keys():
                        contents += [value]
        return contents

class Content:
    def __init__(self, rowid, cmsid, title, view_counter):
        self._rowid = rowid
        self._cmsid = cmsid
        self._title = title
        self._view_counter = view_counter

    @property
    def rowid(self):
        return self._rowid
    @property
    def cmsid(self):
        return self._cmsid
    @property
    def title(self):
        return self._title
    @property
    def view_counter(self):
        return self._view_counter

class ContentsBuilder:
    def __init__(self, contents):
        self._contents = contents

    def build(self):
        return map(
            lambda x: Content(x['_rowid'], x['cmsid'], x['title'], x['view_counter']),
            self._contents
        )

def search(keyword, **option):
    query = SearchQueryBuilder(keyword, **option).build()
    return SearchRequest(query).fetch().contents
