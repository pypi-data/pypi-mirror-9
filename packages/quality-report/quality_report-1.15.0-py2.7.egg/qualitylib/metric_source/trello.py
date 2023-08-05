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
from __future__ import absolute_import


import datetime
import httplib
import logging
import time
import urllib2


from .. import utils, domain


class TrelloUnreachableException(Exception):
    ''' Exception for situations where we can't reach Trello. '''
    pass


class TrelloObject(domain.MetricSource):
    ''' Base class for Trello objects. '''

    url_template = 'https://api.trello.com/1/{object_type}/{object_id}' \
                   '{argument}?key={appkey}&token={token}{parameters}'

    def __init__(self, object_id, appkey, token, urlopen=urllib2.urlopen):
        self._appkey = appkey
        self._token = token
        self.__urlopen = urlopen
        object_type = self.__class__.__name__[len('Trello'):].lower()
        self._parameters = dict(object_type=object_type, object_id=object_id,
                                appkey=appkey, token=token)

    def __nonzero__(self):
        return bool(self._parameters['appkey']) and \
               bool(self._parameters['object_id'])

    def __repr__(self):
        return repr(self._json())

    @utils.memoized
    def _json(self, argument='', extra_parameters=''):
        ''' Return the JSON at url. '''
        parameters = self._parameters.copy()
        parameters.update(dict(argument=argument, parameters=extra_parameters))
        url = self.url_template.format(**parameters)
        try:
            json_string = self.__urlopen(url).read()
        except (urllib2.URLError, httplib.BadStatusLine), reason:
            raise TrelloUnreachableException(reason)
        return utils.eval_json(json_string)

    def name(self):
        ''' Return the name of this Trello object. '''
        return self._json()['name']

    def url(self):
        ''' Return the url of this Trello object. '''
        return self._json()['url']

    def date_of_last_update(self):
        ''' Return the date of the last action at this Trello object. '''
        last_action = self._json(argument='/actions',
                                 extra_parameters='&filter=all')[0]
        return self.date_time_from_string(last_action['date'])

    def last_update_time_delta(self):
        ''' Return the amount of time since the last update. '''
        return datetime.datetime.now() - self.date_of_last_update()

    @staticmethod
    def date_time_from_string(date_time_timezone_string):
        ''' Parse the date/time string representation into a datetime
            instance. Expected format is:
            "<year>-<month>-<day>T<hour>:<minute>:<second>.<timezone>Z". '''
        date_time_string = date_time_timezone_string.split('.')[0]
        year, month, day, hour, minute, second = \
            time.strptime(date_time_string, '%Y-%m-%dT%H:%M:%S')[:6]
        return datetime.datetime(year, month, day, hour, minute, second)


class TrelloCard(TrelloObject):
    ''' Class representing a Trello card. '''

    def due_date_time(self):
        ''' Return the date/time when this card is due or None when the card
            has no due date/time. '''
        json = self._json()
        if 'due' in json:
            date_time_string = json['due']
            if date_time_string:
                return self.date_time_from_string(date_time_string)
        return None

    def over_due_time_delta(self, now=datetime.datetime.now):
        ''' Return the amount of time the card is over due. '''
        if self.due_date_time():
            return now() - self.due_date_time()
        else:
            return datetime.timedelta()

    def is_over_due(self, now=datetime.datetime.now):
        ''' Return whether the card is over due. '''
        due_date_time = self.due_date_time()
        if due_date_time:
            return due_date_time < now()
        else:
            return False

    def is_inactive(self, days, now=datetime.datetime.now):
        ''' Return whether the card has been inactive for the specified number
            of days. '''
        if self.due_date_time() and self.due_date_time() > now():
            return False
        else:
            max_age = datetime.timedelta(days=days)
            return now() - self.date_of_last_update() > max_age


class TrelloBoard(TrelloObject):
    ''' Class representing a Trello board. '''

    def __init__(self, *args, **kwargs):
        self.__card_class = kwargs.pop('card_class', TrelloCard)
        super(TrelloBoard, self).__init__(*args, **kwargs)

    def nr_of_over_due_or_inactive_cards(self, days=14):
        ''' Return the number of (non-archived) cards on this Trello board
            that haven't been updated for the specified number of days or are
            over due. '''
        return len(self.over_due_or_inactive_cards(days))

    @utils.memoized
    def over_due_or_inactive_cards(self, days=14):
        ''' Return the (non-archived) cards on this Trello board that are
            over due or inactive. '''
        return [card for card in self.__cards()
                if card.is_over_due() or card.is_inactive(days)]

    def over_due_or_inactive_cards_url(self, days=14):
        ''' Return the urls for the (non-archived) cards on this Trello board
            that are over due or inactive. '''
        urls = dict()
        for card in self.over_due_or_inactive_cards(days):
            remarks = []
            if card.is_over_due():
                time_delta = utils.format_timedelta(card.over_due_time_delta())
                remarks.append('{time_delta} te laat'.format(time_delta=time_delta))
            if card.is_inactive(days):
                time_delta = utils.format_timedelta(card.last_update_time_delta())
                remarks.append('{time_delta} niet bijgewerkt'.format(time_delta=time_delta))
            label = u'{card} ({remarks})'.format(card=card.name(),
                                                 remarks=u' en '.join(remarks))
            urls[label] = card.url()
        return urls

    @utils.memoized
    def __cards(self):
        ''' Return the (non-archived) cards on this Trello board. '''
        try:
            return [self.__create_card(card['id'])
                    for card in self._json(argument='/cards')]
        except TrelloUnreachableException, reason:
            logging.warning("Couldn't get cards from Trello board: %s", reason)
            return []

    def __create_card(self, card_id):
        ''' Create a Trello card with the specified id. '''
        return self.__card_class(card_id, self._appkey, self._token)


class TrelloActionsBoard(TrelloBoard):
    ''' Actions board in Trello. '''
    metric_source_name = 'Trello actions board'


class TrelloRiskBoard(TrelloBoard):
    ''' Risk log in Trello. '''
    metric_source_name = 'Trello risk board'
