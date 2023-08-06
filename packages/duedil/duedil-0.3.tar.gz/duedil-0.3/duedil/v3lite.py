# -*- coding: utf-8 -*-
#
#  DuedilApiClient 3 Lite
#  @copyright 2014 Christian Ledermann
#
#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.
#

from __future__ import print_function

import json

try:  # pragma: no cover
    # For Python 3.0 and later
    from urllib.parse import urlencode
    from urllib.request import urlopen
except ImportError:  # pragma: no cover
    # Fall back to Python 2's urllib(2)
    from urllib import urlencode
    from urllib2 import urlopen

try:  # pragma: no cover
    long
except NameError:  # pragma: no cover
    # Python 3
    long = int

try:  # pragma: no cover
    unicode
except NameError:  # pragma: no cover
    # Python 3
    basestring = unicode = str


class Company(object):

    _allowed_attributes = [
        'duedil_url',
        # string the url of the full company profile on duedil.com
        'company_number',
        # string the company number
        'name',
        # string the company name
        'name_formated',
        # string a more readable version of the company name
        'registered_address',
        # obj Holds address information about the company
        # 'registered_address.string',
        # string Full registered address of the company, formatted as a
        # string.
        # 'registered_address.postcode',
        # string The postcode (if available) of the company
        # 'registered_address.full_address',
        # array array containing the individual address lines
        'category',
        # string The category of company eg "Public Limited Company"
        'status',
        # string a string describing the status of company eg "In
        # Liquidation"
        'locale',
        # string Either "United Kingdom" or "Republic of Ireland"
        'previous_names',
        # array a collection containing one or more previous name
        # objects
        # 'previous_names[].name',
        # string the raw previous name of the company
        # 'previous_names[].name_formatted',
        # string a more readable version of the previous name
        # 'previous_names[].ended_date',
        # string when the company ceased using this name [YYYY-MM-DD]
        'sic_codes',
        # array a collection containing one or more SIC code objects
        # 'sic_codes[].code',
        # string The SIC code
        # 'sic_codes[].description',
        # string Description of the SIC code
        # 'sic_codes[].type',
        # string Either "primary" or "secondary"
        'incorporation_date',
        # string when the company was incorporated. [YYYY-MM-DD]
        'accounts',
        # obj Information about the most recent accounts
        # 'accounts.accounts_date',
        # string Date of latest accounts. [YYYY-MM-DD]
        # 'accounts.type',
        # string The type of accounts filed. eg "Full"
        'returns',
        # obj information about the company's returns
        # 'returns.last_returns_date',
        # string Date of the last returns. [YYYY-MM-DD]
    ]

    def __init__(self, api_key, company_number, cache=None, **kwargs):
        self.url = 'http://api.duedil.com/open/uk/company/%s' % company_number
        self.api_key = api_key
        self.company_number = company_number
        self._cache = cache
        self._set_attributes(missing=False, **kwargs)

    def _set_attributes(self, missing, **kwargs):
        for k, v in kwargs.items():
            if k not in self._allowed_attributes:
                print ("'%s'," % k)
            # assert(k in self._allowed_attributes)
            self.__setattr__(k, v)
        if missing:
            for allowed in self._allowed_attributes:
                if allowed not in kwargs:
                    self.__setattr__(allowed, None)

    def __getattribute__(self, name):
        """
        lazily return attributes, only contact duedil if necessary
        """
        try:
            return super(Company, self).__getattribute__(name)
        except AttributeError:
            if name in self._allowed_attributes:
                self.get()
                return super(Company, self).__getattribute__(name)
            else:
                raise

    def get(self):
        """
        get results from duedil
        """
        if self._cache is not None:
            result = self._cache.get_url(self.url)
        else:
            result = None
        if result is None:
            data = {'api_key': self.api_key}
            req = urlopen('%s?%s' % (self.url, urlencode(data)))
            result = json.loads(req.read().decode('utf-8'))
            if self._cache is not None:
                self._cache.set_url(self.url, result)
        assert(result.get('company_number') == self.company_number)
        self._set_attributes(missing=True, **result)
        return result


class Client(object):

    RESPONSE_FIELDS = [
        'company_number',
        # string The company number
        'locale',
        # string Either "United Kingdom" or "Republic of Ireland"
        'name',
        # string The company name
        'name_formatted',
        # string a more readable version of the company name
        'link',
        # string url to retrieve the company profile, just add your
        # API key and request.
    ]

    def __init__(self, api_key, cache=None):
        self.api_key = api_key
        self.url = 'http://api.duedil.com/open'
        self.cache = cache

    def search(self, name):
        data = {'q': name, 'api_key': self.api_key}
        req = urlopen('%s/search?%s'
                      % (self.url, urlencode(data)))
        results = json.loads(req.read().decode('utf-8'))
        companies = []
        for r in results['response']['data']:
            companies.append(
                Company(self.api_key, cache=self.cache, **r)
            )
        return companies, results
