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

import unittest

from .cache import Cache
from .v3pro import Company, Director

try:  # pragma: no cover
    from .secrets import PRO_API_KEY as API_KEY
    SANDBOX = False
except ImportError:  # pragma: no cover
    API_KEY = 'x425dum7jp2jxuz7e3ktaqmx'
    SANDBOX = True


class CompanyTestCase(unittest.TestCase):

    if SANDBOX:
        company_id = '7c6338188254b24019a69d14e3158de02d2ce35e'
    else:  # pragma: no cover
        company_id = '06999618'

    def test_get_cached(self):
        cache = Cache()
        company = Company(API_KEY, self.company_id, 'uk', SANDBOX, cache)
        result = company.get()
        rid = result['request_id']
        result = company.get()
        rid2 = result['request_id']
        self.assertEqual(rid, rid2)

    def test_get_uncached(self):
        cache = None
        company = Company(API_KEY, self.company_id, 'uk', SANDBOX, cache)
        result = company.get()
        rid = result['request_id']
        result = company.get()
        rid2 = result['request_id']
        self.assertNotEqual(rid, rid2)


class DirectorTestCase(unittest.TestCase):

    if SANDBOX:
        director_id = '1c6e4767b7100e401da7100f1ae1621e2e7d3c49'
    else:  # pragma: no cover
        director_id = '914039209'

    def test_get_cached(self):
        cache = Cache()
        director = Director(API_KEY, self.director_id, 'uk', SANDBOX, cache)
        result = director.get()
        rid = result['request_id']
        result = director.get()
        rid2 = result['request_id']
        self.assertEqual(rid, rid2)

    def test_get_uncached(self):
        cache = None
        director = Director(API_KEY, self.director_id, 'uk', SANDBOX, cache)
        result = director.get()
        rid = result['request_id']
        result = director.get()
        rid2 = result['request_id']
        self.assertNotEqual(rid, rid2)

    def test_under_get_cached(self):
        cache = Cache()
        director = Director(API_KEY, self.director_id, 'uk', SANDBOX, cache)
        result = director._get('service-addresses')
        rid = result['request_id']
        result = director._get('service-addresses')
        rid2 = result['request_id']
        self.assertEqual(rid, rid2)

    def test_under_get_uncached(self):
        cache = None
        director = Director(API_KEY, self.director_id, 'uk', SANDBOX, cache)
        result = director._get('service-addresses')
        rid = result['request_id']
        result = director._get('service-addresses')
        rid2 = result['request_id']
        self.assertNotEqual(rid, rid2)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CompanyTestCase))
    suite.addTest(unittest.makeSuite(DirectorTestCase))
    return suite

if __name__ == '__main__':
    unittest.main()
