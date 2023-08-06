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

from .v3pro import (Client, Company, Director, DirectorShip, RegisteredAddress,
                    ServiceAddress)

try:  # pragma: no cover
    from .secrets import PRO_API_KEY as API_KEY
    SANDBOX = False
except ImportError:  # pragma: no cover
    API_KEY = 'x425dum7jp2jxuz7e3ktaqmx'
    SANDBOX = True


class ClientTestCase(unittest.TestCase):

    def test_url(self):
        client = Client('abcdef')
        self.assertEqual(client.url, 'http://duedil.io/v3')
        client = Client('abcdef', True)
        self.assertEqual(client.url, 'http://duedil.io/v3/sandbox')
        client = Client('abcdef', False)
        self.assertEqual(client.url, 'http://duedil.io/v3')

    def test_key(self):
        client = Client('abcdef')
        self.assertEqual(client.api_key, 'abcdef')


class SearchCompaniesTestCase(unittest.TestCase):

    client = Client(API_KEY, SANDBOX)

    def test_kwargs(self):
        # you have to search for something
        with self.assertRaises(AssertionError):
            self.client.search_company()
        # search terms are strings
        with self.assertRaises(AssertionError):
            self.client.search_company(location=2)
        # search terms must be a valid filter
        with self.assertRaises(AssertionError):
            self.client.search_company(bla='xx')
        # search ranges have a upper and lower
        # numerical value
        with self.assertRaises(AssertionError):
            self.client.search_company(name=1)
        with self.assertRaises(AssertionError):
            self.client.search_company(employee_count=1)
        with self.assertRaises(AssertionError):
            self.client.search_company(employee_count=[1, 2, 3])
        with self.assertRaises(AssertionError):
            self.client.search_company(employee_count=[2, '100'])
        # and this one must pass:
        if not SANDBOX:  # pragma: no cover
            self.client.search_company(name='ex', employee_count=[0, 100])

    def test_order_by(self):
        with self.assertRaises(AssertionError):
            self.client.search_company(name='ex', order_by='None')
        time.sleep(1)
        self.client.search_company(
            order_by={'field': 'turnover', 'direction': 'desc'},
            name='Ex')

    def test_limit(self):
        with self.assertRaises(AssertionError):
            self.client.search_company(name='ex', limit='0')
        companies = self.client.search_company(name='ex', limit=1)
        self.assertEqual(len(companies), 1)

    def test_offset(self):
        with self.assertRaises(AssertionError):
            self.client.search_company(name='ex', offset='0')
        companies = self.client.search_company(name='ex', offset=50000)
        self.assertEqual(len(companies), 0)

    def test_results(self):
        time.sleep(1)
        companies = self.client.search_company(name='ex')
        for company in companies.items():
            self.assertIsInstance(company, Company)
            break

    def test_results_pagination(self):
        time.sleep(1)
        companies = self.client.search_company(name='ex', limit =2)
        self.assertNotEqual(companies.count(), 2)
        i = 0
        for company in companies.items():
            i += 1
            self.assertIsInstance(company, Company)
            self.assertEqual(len(companies), 2)
            if i > 5:
                break




class SearchDirectorsTestCase(unittest.TestCase):

    client = Client(API_KEY, SANDBOX)

    def test_kwargs(self):
        # you have to search for something
        with self.assertRaises(AssertionError):
            self.client.search_director()
        # search terms are strings
        with self.assertRaises(AssertionError):
            self.client.search_director(gender=2)
        # search terms must be a valid filter
        with self.assertRaises(AssertionError):
            self.client.search_director(bla='xx')
        # search ranges have a upper and lower
        # numerical value
        with self.assertRaises(AssertionError):
            self.client.search_director(name=1)
        with self.assertRaises(AssertionError):
            self.client.search_director(turnover=1)
        with self.assertRaises(AssertionError):
            self.client.search_director(turnover=[1, 2, 3])
        with self.assertRaises(AssertionError):
            self.client.search_director(turnover=[2, '100'])
        # and this one must pass:
        if not SANDBOX:
            time.sleep(1)
            self.client.search_director(name='ex', turnover=[0, 100])

    def test_results(self):
        if not SANDBOX:  # pragma: no cover
            time.sleep(1)
            directors = self.client.search_director(name='John')
            for director in directors.items():
                self.assertIsInstance(director, Director)
                break



class CompanyTestCase(unittest.TestCase):

    if SANDBOX:
        company_id = '7c6338188254b24019a69d14e3158de02d2ce35e'
    else:  # pragma: no cover
        company_id = '06999618'

    def test_get(self):
        time.sleep(1)
        company = Company(API_KEY, self.company_id, 'uk', SANDBOX)
        self.assertEqual(len(company.__dict__), 6)
        self.assertIsInstance(company.get(), dict)
        self.assertNotEqual(len(company.name), 0)
        self.assertEqual(len(company.__dict__), 132)

    def test_init(self):
        company = Company(
            API_KEY, self.company_id, 'uk', SANDBOX, name='DUEDIL LIMITED')
        self.assertEqual(company.name, 'DUEDIL LIMITED')
        self.assertEqual(company.id, self.company_id)
        self.assertEqual(company.locale, 'uk')

    def test_lazy_load(self):
        time.sleep(1)
        company = Company(API_KEY, self.company_id, 'uk', SANDBOX)
        self.assertEqual(len(company.__dict__), 6)
        self.assertNotEqual(len(company.name), 0)
        self.assertEqual(len(company.__dict__), 132)

    def test_invalid_attribute(self):
        time.sleep(1)
        company = Company(API_KEY, self.company_id, 'uk', SANDBOX)
        with self.assertRaises(AttributeError):
            company.no_such_attribute

    def test_traverse_directors(self):
        time.sleep(1)
        company = Company(API_KEY, self.company_id, 'uk', SANDBOX)
        directors = company.directors
        for d in directors:
            self.assertIsInstance(d, Director)
        self.assertNotEqual(len(company.directors), 0)

    def test_registered_address(self):
        time.sleep(1)
        company = Company(API_KEY, self.company_id, 'uk', SANDBOX)
        registered_address = company.registered_address
        self.assertIsInstance(registered_address, RegisteredAddress)
        self.assertEqual(company.registered_address, registered_address)

    def test_service_addresses(self):
        time.sleep(1)
        company = Company(API_KEY, self.company_id, 'uk', SANDBOX)
        service_addresses = company.service_addresses
        for service_address in service_addresses:
            self.assertIsInstance(service_address, ServiceAddress)
            self.assertNotEqual(len(service_address.address1), 0)
        self.assertNotEqual(len(company.service_addresses), 0)

    def test_directorships(self):
        time.sleep(1)
        company = Company(API_KEY, self.company_id, 'uk', SANDBOX)
        directorships = company.directorships
        for directorship in directorships:
            self.assertIsInstance(directorship, DirectorShip)
            self.assertNotEqual(len(directorship.address1), 0)
        self.assertNotEqual(len(company.directorships), 0)

    def test_subsidiaries(self):
        time.sleep(1)
        if SANDBOX:
            company = Company(API_KEY, self.company_id, 'uk', SANDBOX)
        else:  # pragma: no cover
            company = Company(API_KEY, '06051516', 'uk', SANDBOX)
        subsidiaries = company.subsidiaries
        for subsidiary in subsidiaries:
            self.assertIsInstance(subsidiary, Company)
            self.assertNotEqual(len(subsidiary.name), 0)
        self.assertNotEqual(len(company.subsidiaries), 0)

    def test_no_subsidiaries(self):
        time.sleep(1)
        if SANDBOX:
            company = Company(API_KEY,
                              '325401bd2f2ea29373c533eb1587e5fcab36f13b',
                              'uk', SANDBOX)
        else:  # pragma: no cover
            company = Company(API_KEY, self.company_id, 'uk', SANDBOX)
        subsidiaries = company.subsidiaries
        self.assertEqual(subsidiaries, [])
        self.assertEqual(len(company.subsidiaries), 0)

    def test_parent(self):
        time.sleep(1)
        if SANDBOX:
            company = Company(API_KEY, self.company_id, 'uk', SANDBOX)
        else:  # pragma: no cover
            company = Company(API_KEY, '03998387', 'uk', SANDBOX)
        parent = company.parent
        self.assertIsInstance(parent, Company)
        self.assertNotEqual(len(parent.name), 0)
        self.assertNotEqual(len(company.parent.name), 0)

    def test_no_parent(self):
        time.sleep(1)
        if SANDBOX:
            company = Company(API_KEY,
                              '325401bd2f2ea29373c533eb1587e5fcab36f13b',
                              'uk', SANDBOX)
        else:  # pragma: no cover
            company = Company(API_KEY, self.company_id, 'uk', SANDBOX)
        parent = company.parent
        self.assertEqual(parent, None)
        self.assertEqual(company.parent, None)


class DirectorTestCase(unittest.TestCase):

    if SANDBOX:
        director_id = '1c6e4767b7100e401da7100f1ae1621e2e7d3c49'
    else:  # pragma: no cover
        director_id = '914039209'

    def test_get(self):
        time.sleep(1)
        director = Director(API_KEY, self.director_id, 'uk', SANDBOX)
        self.assertEqual(len(director.__dict__), 6)
        self.assertIsInstance(director.get(), dict)
        self.assertNotEqual(len(director.director_url), 0)
        self.assertEqual(len(director.__dict__), 31)

    def test_init(self):
        director = Director(API_KEY, self.director_id, 'uk', SANDBOX,
                            surname='Kimmelman')
        self.assertEqual(director.surname, 'Kimmelman')
        self.assertEqual(director.locale, 'uk')

    def test_lazy_load(self):
        time.sleep(1)
        director = Director(API_KEY, self.director_id, 'uk', SANDBOX)
        self.assertEqual(len(director.__dict__), 6)
        self.assertNotEqual(len(director.surname), 0)
        self.assertEqual(len(director.__dict__), 31)

    def test_service_addresses(self):
        time.sleep(1)
        director = Director(API_KEY, self.director_id, 'uk', SANDBOX)
        service_addresses = director.service_addresses
        for service_address in service_addresses:
            self.assertIsInstance(service_address, ServiceAddress)
            self.assertNotEqual(len(service_address.address1), 0)
        self.assertNotEqual(len(director.service_addresses), 0)

    def test_companies(self):
        time.sleep(1)
        director = Director(API_KEY, self.director_id, 'uk', SANDBOX)
        companies = director.companies
        for company in companies:
            self.assertIsInstance(company, Company)
            self.assertNotEqual(len(company.name), 0)
        self.assertNotEqual(len(director.companies), 0)

    def test_directorships(self):
        time.sleep(1)
        director = Director(API_KEY, self.director_id, 'uk', SANDBOX)
        directorships = director.directorships
        for directorship in directorships:
            self.assertIsInstance(directorship, DirectorShip)
            self.assertNotEqual(len(directorship.address1), 0)
        self.assertNotEqual(len(director.directorships), 0)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ClientTestCase))
    suite.addTest(unittest.makeSuite(SearchCompaniesTestCase))
    suite.addTest(unittest.makeSuite(SearchDirectorsTestCase))
    suite.addTest(unittest.makeSuite(CompanyTestCase))
    suite.addTest(unittest.makeSuite(DirectorTestCase))
    return suite

if __name__ == '__main__':   # pragma: no cover
    unittest.main()
