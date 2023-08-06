# -*- coding: utf-8 -*-
#
#  DuedilApiClient v3 Pro + Credit
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
#


class Cache(object):
    """
    Basic in-memory cache implementation.

    The key-values are stored internally as a dictionary. An existing
    dictionary can be passed to the constructor to initialise.
    """

    _raw_dict = {}

    def __init__(self, raw_dict={}):
        self._raw_dict = raw_dict

    def get_url(self, url):
        """
        get the value in cache or None if URL doesn't match any

        :param url: The URL to query
        :return: the value in cache or None
        """
        return self._raw_dict.get(url, None)

    def set_url(self, url, data):
        """
        Store the data for given URL in cache, override any previously present value

        :param url: The URL as key
        :param data: The value to store
        :return: Nothing
        """
        self._raw_dict[url] = data
