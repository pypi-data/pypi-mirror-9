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

from qualitylib.metric_source import Wiki
from qualitylib.domain import Team
import BeautifulSoup
import datetime
import unittest


class WikiUnderTest(Wiki):
    ''' Override the soup method to return a fixed HTML fragment. '''
    html = '''<table border="1">
                <tr>
                  <th align="right">Datum</th>
                  <th>9-1-2013</th>
                  <th>18-1-2013</th>
                </tr>
                <tr id="team_1">
                    <td>Smiley team 1</td>
                    <td></td><td>:-)</td>
                </tr>
                <tr id="team_2">
                    <td>Smiley 2</td>
                    <td>:-)</td>
                    <td>:-(</td>
                </tr>
              </table>
              <table border="1">
                <tr>
                  <th>Metric ID</th>
                  <th>Comment</th>
                </tr>
                <tr id="metric_id">
                  <td>metric_id</td>
                  <td>Comment</td>
                </tr>
              </table>'''
    
    def soup(self, url):
        return BeautifulSoup.BeautifulSoup(self.html)
    

class WikiTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the Wiki class. '''
    
    def setUp(self):  # pylint: disable=invalid-name
        self.__wiki = WikiUnderTest('http://wiki')
        
    def test_url(self):
        ''' Test that the url is correct. '''
        self.assertEqual('http://wiki', self.__wiki.url())

    def test_comment_url(self):
        ''' Test that the comment url is correct. '''
        self.assertEqual('http://wiki', self.__wiki.comment_url())

    def test_team_spirit(self):
        ''' Test the spirit of the team. '''
        self.assertEqual(':-(', self.__wiki.team_spirit('team_2'))

    def test_missing_team_spirit(self):
        ''' Test exception when team is missing. '''
        self.assertRaises(IndexError, self.__wiki.team_spirit, 'missing')

    def test_date_of_last_measurement(self):
        ''' Test the date of the last measurement of the spirit of the team. '''
        self.assertEqual(datetime.datetime(2013, 1, 18), 
            self.__wiki.date_of_last_team_spirit_measurement('team_2'))

    def test_no_comment(self):
        ''' Test that the comment is empty for a metric that is not in the 
            comment table. '''
        self.assertFalse(self.__wiki.comment('missing_id'))

    def test_comment(self):
        ''' Test that the comment from the wiki is returned. '''
        self.assertEqual('Comment', self.__wiki.comment('metric_id'))
