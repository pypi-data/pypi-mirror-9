'''
Copyright 2012-2014 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

from qualitylib import domain
import unittest


class StreetTest(unittest.TestCase):  # pylint: disable=too-many-public-methods
    ''' Unit tests for the Street domain class. '''
    def setUp(self):  # pylint: disable=C0103
        self.__street = domain.Street('street_a.*', name='Street A')

    def test_str(self):
        ''' Test that the string formatting of a street equals the street 
            name. '''
        self.assertEqual(self.__street.id_string(), str(self.__street))

    def test_id_string(self):
        ''' Test that the id string for the street does not contain spaces. '''
        self.assertEqual('street_a', self.__street.id_string())
