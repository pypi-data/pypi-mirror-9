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

import unittest
from qualitylib.domain.measurement.measurable import MeasurableObject
from qualitylib.domain import TechnicalDebtTarget, Team


class MeasurableObjectTests(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the measurable object. '''
    def setUp(self):  # pylint: disable=invalid-name
        self.__measurable = MeasurableObject(targets={self.__class__: 100},
            low_targets={self.__class__: 50},
            technical_debt_targets={self.__class__: 
                                    TechnicalDebtTarget(100, 'explanation')},
            metric_source_ids={self.__class__: 'id'},
            old_metric_source_ids={self.__class__: {'1': 'old_id'}},
            metric_source_options={self.__class__: 'options'},
            metric_options={self.__class__: 'metric options'},
            responsible_teams=[Team(name='A')])

    def test_no_target(self):
        ''' Test that there is no target for an unknown class. '''
        self.assertFalse(self.__measurable.target(''.__class__))

    def test_target(self):
        ''' Test the target for a known class. '''
        self.assertEqual(100, self.__measurable.target(self.__class__))

    def test_no_low_target(self):
        ''' Test that there is no low target for an unknown class. '''
        self.assertFalse(self.__measurable.low_target(''.__class__))

    def test_low_target(self):
        ''' Test the low target for a known class. '''
        self.assertEqual(50, self.__measurable.low_target(self.__class__))

    def test_no_technical_debt(self):
        ''' Test that there is no technical debt for an unknown class. '''
        self.assertFalse(self.__measurable.technical_debt_target(''.__class__))

    def test_technical_debt(self):
        ''' Test the technical debt for a known class. '''
        target = self.__measurable.technical_debt_target(self.__class__)
        self.assertEqual(100, target.target_value())

    def test_no_metric_source_id(self):
        ''' Test the metric source id for an unknown class. '''
        self.assertFalse(self.__measurable.metric_source_id(''.__class__))

    def test_metric_source_id(self):
        ''' Test the metric source id for a known class. '''
        self.assertEqual('id', 
                         self.__measurable.metric_source_id(self.__class__))

    def test_no_old_metric_source_id(self):
        ''' Test the old metric source id for an unknown class. '''
        self.assertFalse(self.__measurable.old_metric_source_id(''.__class__, '1'))

    def test_old_metric_source_id(self):
        ''' Test the old metric source id for a known class and version. '''
        self.assertEqual('old_id',
                         self.__measurable.old_metric_source_id(self.__class__,
                                                                '1'))

    def test_old_metric_source_id_unknown_version(self):
        ''' Test the old metric source id for a known class but an unknown 
            version. '''
        self.assertFalse(self.__measurable.old_metric_source_id(self.__class__, '2'))

    def test_no_metric_source_option(self):
        ''' Test the metric source option for an unknown class. '''
        self.assertFalse(self.__measurable.metric_source_options(''.__class__))

    def test_metric_source_options(self):
        ''' Test the metric source options for a known class. '''
        self.assertEqual('options', 
            self.__measurable.metric_source_options(self.__class__))

    def test_no_metric_option(self):
        ''' Test the metric option for an unknown class. '''
        self.assertFalse(self.__measurable.metric_options(''.__class__))

    def test_metric_options(self):
        ''' Test the metric options for a known class. '''
        self.assertEqual('metric options', 
                         self.__measurable.metric_options(self.__class__))

    def test_responsible_teams(self):
        ''' Test that the street has responsible teams. '''
        self.assertEqual([Team(name='A')],
                         self.__measurable.responsible_teams())
