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

from qualitylib.domain import TechnicalDebtTarget, DynamicTechnicalDebtTarget
from qualitylib.utils import format_date
import unittest
import datetime


class TechnicalDebtTargetTests(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the technical debt target class. '''

    def test_target_value(self):
        ''' Test that the target value can be retrieved. '''
        self.assertEqual(10, TechnicalDebtTarget(10).target_value())
 
    def test_explanation(self):
        ''' Test that the explanation for the technical debt can be 
            retrieved. '''
        self.assertEqual('De op dit moment geaccepteerde technische schuld ' \
                         'is 10. Explanation', 
                         TechnicalDebtTarget(10, 'Explanation').explanation())
        
    def test_unit(self):
        ''' Test that the explanation for the technical debt includes the 
            unit. '''
        self.assertEqual('De op dit moment geaccepteerde technische schuld ' \
                         'is 10 LOC. Explanation', 
                         TechnicalDebtTarget(10, 'Explanation', 
                                             'LOC').explanation())
        
    def test_percentage_unit(self):
        ''' Test that the percentage has no space before it. '''
        self.assertEqual('De op dit moment geaccepteerde technische schuld ' \
                         'is 10%. Explanation', 
                         TechnicalDebtTarget(10, 'Explanation', 
                                             '%').explanation())
        
        
class DynamicTechnicalDebtTargetTests(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the dynamically changing technical debt target class. '''

    def test_before_initial_date(self):
        ''' Test that the target value equals the initial target value if the
            current date is before the initial date. '''
        now = datetime.datetime.now()
        target = DynamicTechnicalDebtTarget( \
                                    100, now + datetime.timedelta(days=10), 
                                    200, now + datetime.timedelta(days=20))
        self.assertEqual(100, target.target_value())

    def test_at_initial_date(self):
        ''' Test that the target value equals the initial target value if the
            current date is at the initial date. '''
        now = datetime.datetime.now()
        target = DynamicTechnicalDebtTarget( \
                                    100, now, 
                                    200, now + datetime.timedelta(days=20))
        self.assertEqual(100, target.target_value())
                
    def test_after_end_date(self):
        ''' Test that the target value equals the end target value if the
            current date is after the end date. '''
        now = datetime.datetime.now()
        target = DynamicTechnicalDebtTarget( \
                                    100, now - datetime.timedelta(days=20), 
                                    200, now - datetime.timedelta(days=10))
        self.assertEqual(200, target.target_value())

    def test_at_end_date(self):
        ''' Test that the target value equals the end target value if the
            current date is at the end date. '''
        now = datetime.datetime.now()
        target = DynamicTechnicalDebtTarget( \
                                    100, now - datetime.timedelta(days=20), 
                                    200, now)
        self.assertEqual(200, target.target_value())
        
    def test_halfway(self):
        ''' Test that the target value is half way the initial target value and
            the end target value if the current date is half way. '''
        now = datetime.datetime.now()
        target = DynamicTechnicalDebtTarget( \
                                    100, now - datetime.timedelta(days=10), 
                                    200, now + datetime.timedelta(days=10))
        self.assertEqual(150, target.target_value())

    def test_default_explanation(self):
        ''' Test that the default explanation shows the period. '''
        now = datetime.datetime.now()
        start = now - datetime.timedelta(days=10)
        end = now + datetime.timedelta(days=10)
        target = DynamicTechnicalDebtTarget(200, start, 100, end, unit='LOC')
        self.assertEqual('Het doel is dat de technische schuld vermindert ' \
                         'van %s LOC op %s naar %s LOC op %s. De op dit ' \
                         'moment geaccepteerde technische schuld is %s LOC.' % \
                         (200, format_date(start, year=True), 100, 
                          format_date(end, year=True), target.target_value()), 
                         target.explanation())

    def test_custom_explanation(self):
        ''' Test that the custom explanation is added to the default 
            explanation. '''
        now = datetime.datetime.now()
        start = now - datetime.timedelta(days=10)
        end = now + datetime.timedelta(days=10)
        target = DynamicTechnicalDebtTarget(200, start, 100, end, 'Extra.')
        self.assertEqual('Het doel is dat de technische schuld vermindert '
                         'van %s op %s naar %s op %s. De op dit moment '\
                         'geaccepteerde technische schuld is %s. Extra.' % (200,
                                format_date(start, year=True), 100, 
                                format_date(end, year=True),
                                target.target_value()), 
                         target.explanation())
