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

from qualitylib.metric_source import TrelloBoard
from qualitylib.metric_source.trello import TrelloCard
import StringIO
import datetime
import unittest
import urllib2


class FakeCard(object):
    ''' Fake card class to use for testing the Trello board class. '''
    def __init__(self, card_id, *args, **kwargs): 
        # pylint: disable=unused-argument
        self.__card_id = card_id
        # The card id determines the status of the fake card:
        self.__over_due = card_id in (1, 3)
        self.__inactive = card_id in (2, 3)
        
    def name(self):
        '''Return the name of the card. '''
        return 'card %d' % self.__card_id
    
    def url(self):
        ''' Return the url of the card. '''
        return 'http://card/%d' % self.__card_id
    
    def is_over_due(self):
        ''' Return whether this card is over due. '''
        return self.__over_due
    
    def over_due_time_delta(self):
        ''' Return how much over due the card is. '''
        return datetime.timedelta(days=3 if self.__over_due else 0)
    
    def is_inactive(self, days):  # pylint: disable=unused-argument
        ''' Return whether this card has been inactive for the specified 
            number of days. '''
        return self.__inactive
    
    def last_update_time_delta(self):
        ''' Return the time since the last update. '''
        return datetime.timedelta(days=4 if self.__inactive else 0)


class TrelloBoardTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the Trello board class. '''
    
    def setUp(self):  # pylint: disable=invalid-name
        self.__raise = False
        self.__cards_json = ''
        self.__trello_board = TrelloBoard('object_id', 'appkey', 'token', 
                                          urlopen=self.__urlopen,
                                          card_class=FakeCard)
    
    def __urlopen(self, url):
        ''' Return a fake JSON string. '''
        if self.__raise:
            raise urllib2.URLError(url)
        if 'cards' in url:
            json = self.__cards_json
        else:
            json = '{"url": "%s"}' % url
        return StringIO.StringIO(json)
        
    def test_url(self):
        ''' Test the url of the Trello board. '''
        self.assertEqual('https://api.trello.com/1/board/object_id?' \
                         'key=appkey&token=token', self.__trello_board.url())
    
    def test_one_over_due(self):
        ''' Test the count with one over due card. '''
        self.__cards_json = '[{"id": 1}]'
        self.assertEqual(1, 
                         self.__trello_board.nr_of_over_due_or_inactive_cards())
        
    def test_one_over_due_url(self):
        ''' Test the url for one over due card. '''
        self.__cards_json = '[{"id": 1}]'
        self.assertEqual({'card 1 (3 dagen te laat)': 'http://card/1'}, 
                         self.__trello_board.over_due_or_inactive_cards_url())
        
    def test_one_inactive(self):
        '''Test the count with one inactive card. '''
        self.__cards_json = '[{"id": 2}]'
        self.assertEqual(1, 
                         self.__trello_board.nr_of_over_due_or_inactive_cards())

    def test_one_inactive_url(self):
        ''' Test the url for one inactive card. '''
        self.__cards_json = '[{"id": 2}]'
        self.assertEqual({'card 2 (4 dagen niet bijgewerkt)': 'http://card/2'}, 
                         self.__trello_board.over_due_or_inactive_cards_url())
        
    def test_one_over_due_and_inactive(self):
        ''' Test the count with one inactive and over due card. '''
        self.__cards_json = '[{"id": 3}]'
        self.assertEqual(1, 
                         self.__trello_board.nr_of_over_due_or_inactive_cards())

    def test_one_over_due_and_inactive_url(self):
        ''' Test the url for one inactive and over due card. '''
        self.__cards_json = '[{"id": 3}]'
        self.assertEqual({'card 3 (3 dagen te laat en 4 dagen niet ' \
                          'bijgewerkt)': 'http://card/3'}, 
                         self.__trello_board.over_due_or_inactive_cards_url())
        
    def test_one_inactive_and_one_over_due(self):
        ''' Test the count with one inactive and one over due card. '''
        self.__cards_json = '[{"id": 1}, {"id": 2}]'
        self.assertEqual(2, 
                         self.__trello_board.nr_of_over_due_or_inactive_cards())

    def test_one_inactive_and_one_over_due_url(self):
        ''' Test the url for one inactive card and over due card. '''
        self.__cards_json = '[{"id": 1}, {"id": 2}]'
        self.assertEqual({'card 1 (3 dagen te laat)': 'http://card/1',
                          'card 2 (4 dagen niet bijgewerkt)': 'http://card/2'}, 
                         self.__trello_board.over_due_or_inactive_cards_url())

    def test_no_cards_url(self):
        ''' Test the url for over due or inactive cards when there are no 
            cards. '''
        self.__cards_json = '{}'
        self.assertEqual({}, 
                         self.__trello_board.over_due_or_inactive_cards_url())

    def test_one_active_card(self):
        ''' Test the url for one active card. '''
        self.__cards_json = '[{"id": 0}]'
        self.assertEqual({}, 
                         self.__trello_board.over_due_or_inactive_cards_url())
        
    def test_http_error(self):
        ''' Test dealing with http errors when retrieving the JSON. '''
        self.__raise = True
        self.assertEqual(0, 
                         self.__trello_board.nr_of_over_due_or_inactive_cards())


class TrelloCardTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the Trello card class. '''
    
    def setUp(self):  # pylint: disable=invalid-name
        self.__raise = False
        self.__json = '{}'
        self.__trello_card = TrelloCard('object_id', 'appkey', 'token', 
                                        urlopen=self.__urlopen)
    
    def __urlopen(self, url):  # pylint: disable=unused-argument
        ''' Return a fake JSON string. '''
        return StringIO.StringIO(self.__json)
    
    def test_no_due_date_time(self):
        ''' Test that an empty card has no due date time. '''
        self.assertEqual(None, self.__trello_card.due_date_time())
    
    def test_due_date_time(self):
        ''' Test the due date time. '''
        self.__json = '{"due": "2013-5-4T16:45:33.09Z"}'
        self.assertEqual(datetime.datetime(2013, 5, 4, 16, 45, 33), 
                         self.__trello_card.due_date_time())

    def test_over_due_time_delta(self):
        ''' Test the age of an over due card. '''
        def now():
            return datetime.datetime(2014, 5, 4, 17, 45, 33)
        self.__json = '{"due": "2014-5-4T16:45:33.09Z"}'
        self.assertEqual(datetime.timedelta(hours=1),
                         self.__trello_card.over_due_time_delta(now=now))

    def test_no_over_due_time_delta(self):
        ''' Test the age of a card without due date. '''
        self.assertEqual(datetime.timedelta(),
                         self.__trello_card.over_due_time_delta())

    def test_is_over_due(self):
        ''' Test that an over due card is over due. '''
        def now():
            return datetime.datetime(2014, 5, 4, 17, 45, 33)
        self.__json = '{"due": "2014-5-4T16:45:33.09Z"}'
        self.assertTrue(self.__trello_card.is_over_due(now=now))

    def test_is_not_over_due(self):
        ''' Test that a card with a due date in the future is not over due. '''
        def now():
            return datetime.datetime(2013, 5, 4, 17, 45, 33)
        self.__json = '{"due": "2014-5-4T16:45:33.09Z"}'
        self.assertFalse(self.__trello_card.is_over_due(now=now))

    def test_not_inactive_when_future_due_date(self):
        ''' Test that a card with a due date in the future is not inactive. '''
        def now():
            return datetime.datetime(2013, 5, 4, 17, 45, 33)
        self.__json = '{"due": "2014-5-4T16:45:33.09Z"}'
        self.assertFalse(self.__trello_card.is_inactive(15, now=now))

    def test_not_inactive_when_recently_updated(self):
        ''' Test that a card is not inactive when it has been updated
            recently. '''
        def now():
            return datetime.datetime(2014, 5, 4, 17, 45, 33)
        self.__json = '[{"date": "2014-5-4T16:45:33.09Z"}]'
        self.assertFalse(self.__trello_card.is_inactive(15, now=now))
