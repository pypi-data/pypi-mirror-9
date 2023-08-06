# -*- coding: utf-8 -*-
#
#  DuedilApiClient v3 Pro
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

from .apiconst import (COMPANY_ALLOWED_ATTRIBUTES, COMPANY_RANGE_FILTERS,
                       COMPANY_TERM_FILTERS, DIRECTOR_ALLOWED_ATTRIBUTES,
                       DIRECTOR_RANGE_FILTERS, DIRECTOR_TERM_FILTERS,
                       DIRECTORSHIPS_ALLOWED_ATTRIBUTES,
                       REGISTERED_ADDRESS_ALLOWED_ATTRIBUTES,
                       SERVICE_ADDRESS_ALLOWED_ATTRIBUTES)

try:  # pragma: no cover
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import urlencode
    from urllib.request import urlopen
except ImportError:  # pragma: no cover
    # Fall back to Python 2's urllib(2)
    from urllib import urlencode
    from urllib2 import urlopen, HTTPError

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


class _EndPoint(object):

    def __init__(self, api_key, id, locale, sandbox=False, cache=None,
                 **kwargs):
        self.id = id
        assert(locale in ['uk', 'roi'])
        self.locale = locale
        self.api_key = api_key
        self.sandbox = sandbox
        self._cache = cache
        self._set_attributes(missing=False, **kwargs)

    def _get(self, endpoint):
        url = '%s/%s' % (self.url, endpoint)
        if self._cache is not None:
            result = self._cache.get_url(url)
        else:
            result = None
        if result is None:
            data = {'api_key': self.api_key}
            req = urlopen('%s?%s' % (url, urlencode(data)))
            result = json.loads(req.read().decode('utf-8'))
            if self._cache is not None:
                self._cache.set_url(url, result)
        return result

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
            return super(_EndPoint, self).__getattribute__(name)
        except AttributeError:
            if name in self._allowed_attributes:
                self.get()
                return super(_EndPoint, self).__getattribute__(name)
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
            data = {'api_key': self.api_key, 'nullValue': None}
            req = urlopen('%s?%s' % (self.url, urlencode(data)))
            result = json.loads(req.read().decode('utf-8'))
            if self._cache is not None:
                self._cache.set_url(self.url, result)
        assert(result['response'].get('id') == self.id)
        self._set_attributes(missing=True, **result['response'])
        return result

    @property
    def url(self):
        return self._url


class ResultSet(object):

    def __init__(self, cls, url, api_key, sandbox=False, cache=None):
        self.cls = cls
        self._results = self._get_results(url)
        self._url = url
        self.api_key = api_key
        self.sandbox = sandbox
        self.cache = cache

    def __len__(self):
        return len(self._results['response']['data'])

    def _get_results(self, url):
        # XXX caching should be applied here
        req = urlopen(url)
        results = json.loads(req.read().decode('utf-8'))
        return results

    @property
    def _next_url(self):
        url = self._results['response']['pagination'].get('next_url')
        if url:
            return '%s&api_key=%s' % (url, self.api_key)

    def count(self):
        return self._results['response']['pagination']['total']

    def items(self):
        for r in self._results['response']['data']:
            yield self.cls(self.api_key, sandbox=self.sandbox,
                           cache=self.cache, **r)
        while self._next_url:
            self._results = self._get_results(self._next_url)
            for r in self._results['response']['data']:
                yield self.cls(self.api_key, sandbox=self.sandbox,
                               cache=self.cache, **r)


class ServiceAddress(_EndPoint):

    _name = 'service-addresses'
    _allowed_attributes = SERVICE_ADDRESS_ALLOWED_ATTRIBUTES

    def __init__(self, api_key, id, locale, sandbox=False, cache=None,
                 **kwargs):
        super(ServiceAddress, self).__init__(api_key, id, locale, sandbox,
                                             cache, **kwargs)
        if sandbox:
            url = 'http://duedil.io/v3/sandbox/%s/companies/%s/%s'
            self._url = url % (locale, id, self._name)
        else:  # pragma: no cover
            url = 'http://duedil.io/v3/%s/companies/%s/%s'
            self._url = url % (locale, id, self._name)


class RegisteredAddress(_EndPoint):

    _name = 'registered-address'
    _allowed_attributes = REGISTERED_ADDRESS_ALLOWED_ATTRIBUTES

    def __init__(self, api_key, id, locale, sandbox=False, cache=None,
                 **kwargs):
        super(RegisteredAddress, self).__init__(api_key, id, locale, sandbox,
                                                cache, **kwargs)
        if sandbox:
            url = 'http://duedil.io/v3/sandbox/%s/companies/%s/%s'
            self._url = url % (locale, id, self._name)
        else:  # pragma: no cover
            url = 'http://duedil.io/v3/%s/companies/%s/%s'
            self._url = url % (locale, id, self._name)


class DirectorShip(_EndPoint):

    _name = 'directorships'
    _allowed_attributes = DIRECTORSHIPS_ALLOWED_ATTRIBUTES

    def __init__(self, api_key, id, locale, sandbox=False, cache=None,
                 **kwargs):
        super(DirectorShip, self).__init__(api_key, id, locale, sandbox,
                                           cache, **kwargs)
        if sandbox:
            url = 'http://duedil.io/v3/sandbox/%s/directors/%s/%s'
            self._url = url % (locale, id, self._name)
        else:  # pragma: no cover
            url = 'http://duedil.io/v3/%s/directors/%s/%s'
            self._url = url % (locale, id, self._name)


class Director(_EndPoint):

    _name = 'director'
    _service_addresses = None
    _companies = None
    _directorships = None

    _allowed_attributes = DIRECTOR_ALLOWED_ATTRIBUTES

    def __init__(self, api_key, id, locale, sandbox=False, cache=None,
                 **kwargs):
        super(Director, self).__init__(api_key, id, locale, sandbox,
                                       cache, **kwargs)
        if sandbox:
            self._url = 'http://duedil.io/v3/sandbox/%s/directors/%s' % (
                locale, id)
        else:  # pragma: no cover
            self._url = 'http://duedil.io/v3/%s/directors/%s' % (locale, id)

    @property
    def service_addresses(self):
        if self._service_addresses:
            return self._service_addresses
        else:
            results = self._get('service-addresses')
            address_list = []
            for r in results['response']['data']:
                r['locale'] = r.get('locale', self.locale)
                address_list.append(
                    ServiceAddress(self.api_key,
                                   sandbox=self.sandbox,
                                   **r)
                )
            self._service_addresses = address_list
        return self._service_addresses

    @property
    def companies(self):
        if self._companies:
            return self._companies
        else:
            results = self._get('companies')
            company_list = []
            for r in results['response']['data']:
                r['locale'] = r.get('locale', self.locale)
                company_list.append(
                    Company(self.api_key,
                            sandbox=self.sandbox, **r)
                )
            self._companies = company_list
        return self._companies

    @property
    def directorships(self):
        if self._directorships:
            return self._directorships
        else:
            results = self._get('directorships')
            directorships_list = []
            for r in results['response']['data']:
                if not r.get('locale'):
                    r['locale'] = self.locale
                directorships_list.append(
                    DirectorShip(self.api_key,
                                 sandbox=self.sandbox, **r)
                )
            self._directorships = directorships_list
        return self._directorships


class Company(_EndPoint):

    _name = 'company'
    _service_addresses = None
    _directorships = None
    _directors = None
    _registered_address = None
    _subsidiaries = None
    _parent = None
    _has_parent = None
    _allowed_attributes = COMPANY_ALLOWED_ATTRIBUTES

    def __init__(self, api_key, id, locale, sandbox=False, cache=None,
                 **kwargs):
        super(Company, self).__init__(api_key, id, locale, sandbox,
                                      cache, **kwargs)
        if sandbox:
            self._url = 'http://duedil.io/v3/sandbox/%s/companies/%s' % (
                locale, id)
        else:  # pragma: no cover
            self._url = 'http://duedil.io/v3/%s/companies/%s' % (locale, id)

    @property
    def directors(self):
        if self._directors:
            return self._directors
        else:
            results = self._get('directors')
            director_list = []
            for r in results['response']['data']:
                r['locale'] = r.get('locale', self.locale)
                director_list.append(
                    Director(self.api_key,
                             sandbox=self.sandbox, **r)
                )
            self._directors = director_list
        return self._directors

    @property
    def registered_address(self):
        if self._registered_address:
            return self._registered_address
        else:
            results = self._get('registered-address')
            address_data = results['response']
            self._registered_address = RegisteredAddress(self.api_key,
                                                         locale=self.locale,
                                                         sandbox=self.sandbox,
                                                         **address_data)
            return self._registered_address

    @property
    def service_addresses(self):
        if self._service_addresses:
            return self._service_addresses
        else:
            results = self._get('service-addresses')
            address_list = []
            for r in results['response']['data']:
                address_list.append(
                    ServiceAddress(self.api_key, id=self.id,
                                   locale=self.locale,
                                   sandbox=self.sandbox,
                                   **r)
                )
            self._service_addresses = address_list
        return self._service_addresses

    @property
    def directorships(self):
        if self._directorships:
            return self._directorships
        else:
            results = self._get('directorships')
            directorships_list = []
            for r in results['response']['data']:
                r['locale'] = r.get('locale', self.locale)
                directorships_list.append(
                    DirectorShip(self.api_key,
                                 sandbox=self.sandbox, **r)
                )
            self._directorships = directorships_list
        return self._directorships

    @property
    def subsidiaries(self):
        if isinstance(self._subsidiaries, (list, tuple)):
            return self._subsidiaries
        else:
            subsidiaries_list = []
            try:
                results = self._get('subsidiaries')
                for r in results['response']['data']:
                    r['locale'] = r.get('locale', self.locale)
                    subsidiaries_list.append(
                        Company(self.api_key,
                                sandbox=self.sandbox, **r)
                    )
            except HTTPError as e:
                if e.code == 404:
                    pass
                else:
                    raise
            self._subsidiaries = subsidiaries_list
        return self._subsidiaries

    @property
    def parent(self):
        if self._has_parent is not None:
            return self._parent
        else:
            try:
                results = self._get('parent')
                p_data = results['response']
                p_data['locale'] = p_data.get('locale', self.locale)
                self._parent = Company(self.api_key,
                                       sandbox=self.sandbox, **p_data)
                self._has_parent = True
            except HTTPError as e:
                if e.code == 404:
                    self._has_parent = False
                else:
                    raise
        return self._parent

    '''
    previous-company-names
    industries
    shareholders
    bank-accounts
    accounts
    documents
    mortgages
    '''


class Client(object):

    def __init__(self, api_key, sandbox=False, cache=None):
        self.api_key = api_key
        self.sandbox = sandbox
        if sandbox:
            self._url = 'http://duedil.io/v3/sandbox'
        else:
            self._url = 'http://duedil.io/v3'
        self.cache = cache

    @property
    def url(self):
        return self._url

    def _build_search_string(self, term_filters, range_filters,
                             order_by=None, limit=None, offset=None,
                             **kwargs):
        data = {'api_key': self.api_key}
        assert(kwargs)
        for arg in kwargs:
            assert(arg in term_filters + range_filters)
            if arg in term_filters:
                # this must be  a string
                assert(isinstance(kwargs[arg], basestring))
            elif arg in COMPANY_RANGE_FILTERS:
                # array of two numbers
                assert(isinstance(kwargs[arg], (list, tuple)))
                assert(len(kwargs[arg]) == 2)
                for v in kwargs[arg]:
                    assert(isinstance(v, (int, long, float)))
        data['filters'] = json.dumps(kwargs)
        if order_by:
            assert(isinstance(order_by, dict))
            assert('field' in order_by)
            assert(
                order_by['field'] in term_filters + range_filters)
            if order_by.get('direction'):
                assert(order_by['direction'] in ['asc', 'desc'])
            data['orderBy'] = json.dumps({order_by['field']:order_by['direction']})
        if limit:
            assert(isinstance(limit, int))
            data['limit'] = limit
        if offset:
            assert(isinstance(offset, int))
            data['offset'] = offset
        return data

    def search_company(self, order_by=None, limit=None, offset=None, **kwargs):
        '''
        Conduct advanced searches across all companies registered in
        UK & Ireland.
        Apply any combination of 44 different filters

        The parameter filters supports two different types of queries:

        * the “range” type (ie, a numeric range) and
        * the “terms” type (for example, an individual company name).

        For the range filter, you have to pass an array;
        for the terms filter, you just pass a string.

        The range type is used when you want to limit the results to a
        particular range of results.

        You can order the results based on the ranges using the
        parameter orderBy.
        '''
        data = self._build_search_string(COMPANY_TERM_FILTERS,
                                         COMPANY_RANGE_FILTERS,
                                         order_by=order_by, limit=limit,
                                         offset=offset, **kwargs)
        url = '%s/companies?%s' % (self.url, urlencode(data))
        results = ResultSet(Company, url, self.api_key,
                            sandbox=self.sandbox, cache=self.cache)
        return results

    def search_director(self, order_by=None, limit=None, offset=None,
                        **kwargs):
        '''
        This “Director search endpoint” is similar to the
        “Company search endpoint”, though with some different ranges and
        terms.

        Searching by financial range will return directors who have a
        directorship at a company fulfilling that range.

        NB: The location filter is not (yet) available for director search.
        '''
        data = self._build_search_string(DIRECTOR_TERM_FILTERS,
                                         DIRECTOR_RANGE_FILTERS,
                                         order_by=order_by, limit=limit,
                                         offset=offset, **kwargs)
        url = '%s/directors?%s' % (self.url, urlencode(data))
        results = ResultSet(Director, url, self.api_key,
                            sandbox=self.sandbox, cache=self.cache)
        return results
