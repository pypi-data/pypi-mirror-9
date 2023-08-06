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

import time
import unittest

from .cache import Cache
from .v3lite import Client, Company

API_KEY = 'hnkc6ew2pbua2mf296kq8yaa'


class SearchCompaniesTestCase(unittest.TestCase):

    client = Client(API_KEY)

    def test_search(self):
        time.sleep(1)
        companies, raw = self.client.search('DueDil')
        self.assertIsInstance(raw, dict)
        for company in companies:
            self.assertIsInstance(company, Company)


class CompanyTestCase(unittest.TestCase):

    def test_init(self):
        response = {'locale': 'United Kingdom',
                    'uri': 'http://api.duedil.com/open/uk/company/06999618',
                    'company_number': '06999618',
                    'name': 'Duedil Limited'}
        company = Company(API_KEY, **response)
        self.assertEqual(company.company_number, '06999618')
        self.assertEqual(company.name, 'Duedil Limited')
        self.assertEqual(company.locale, 'United Kingdom')

    def test_lazy_load(self):
        time.sleep(1)
        company = Company(API_KEY, company_number='03122984')
        self.assertEqual(len(company.__dict__), 4)
        self.assertNotEqual(len(company.category), 0)
        self.assertEqual(len(company.__dict__), 17)
        self.assertEqual(company.name, 'DUE DILIGENCE LIMITED')
        postcode = company.registered_address['postcode']
        self.assertEqual(postcode, 'EX1 2ND')

    def test_cache(self):
        time.sleep(1)
        cache = Cache()
        company = Company(API_KEY, company_number='03008575', cache=cache)
        self.assertIsNone(cache.get_url(company.url))
        self.assertIsInstance(company.get(), dict)
        self.assertIsInstance(cache.get_url(company.url), dict)
        self.assertEqual(company.get(), cache.get_url(company.url))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CompanyTestCase))
    return suite

if __name__ == '__main__':   # pragma: no cover
    unittest.main()
