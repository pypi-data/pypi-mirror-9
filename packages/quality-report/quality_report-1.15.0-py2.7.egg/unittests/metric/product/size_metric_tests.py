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
from qualitylib import metric, domain, metric_source, requirement


class FakeSonar(object):
    ''' Provide for a fake Sonar object so that the unit test don't need 
        access to an actual Sonar instance. '''
    # pylint: disable=unused-argument

    @staticmethod
    def dashboard_url(*args):  
        ''' Return a fake dashboard url. '''
        return 'http://sonar'

    url = dashboard_url

    @staticmethod
    def ncloc(*args):
        ''' Return the number of non-comment LOC. '''
        return 123


class FakeHistory(object):  # pylint: disable=too-few-public-methods
    ''' Fake the history for testing purposes. '''
    @staticmethod  # pylint: disable=unused-argument
    def recent_history(*args):
        ''' Return a fake recent history. '''
        return [100, 200]


class ProductLOCTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the product LOC metric. '''

    def setUp(self):  # pylint: disable=invalid-name
        project = domain.Project(
            metric_sources={metric_source.Sonar: FakeSonar()})
        subject = domain.Product(project, 'PR', name='FakeSubject')
        self._metric = metric.ProductLOC(subject=subject, project=project)

    def test_value(self):
        ''' Test that the value of the metric equals the NCLOC returned by
            Sonar. '''
        self.assertEqual(FakeSonar().ncloc(), self._metric.value())

    def test_url(self):
        ''' Test that the url is correct. '''
        self.assertEqual(dict(Sonar=FakeSonar().dashboard_url()), 
                         self._metric.url())


class TotalLOCTest(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    ''' Unit tests for the total LOC metric. '''

    def setUp(self):  # pylint: disable=invalid-name
        sonar = FakeSonar()
        project = domain.Project(
            metric_sources={metric_source.Sonar: sonar,
                            metric_source.History: FakeHistory()})
        product = domain.Product(project, 'PR', name='FakeSubject',
                                 metric_source_ids={sonar: 'sonar id'})
        product_without_sonar_id = domain.Product(project, 'PW',
                                                  name='ProductWithoutSonarId')
        project.add_product(product)
        # Add products that should be ignored:
        project.add_product(product_without_sonar_id)
        project.add_product_with_version('FakeSubject', '1.1')
        self.__metric = metric.TotalLOC(project=project)

    def test_value(self):
        ''' Test that the value of the metric equals the sum of the NCLOC 
            returned by Sonar. '''
        self.assertEqual(FakeSonar().ncloc(), self.__metric.value())
 
    def test_url(self):
        ''' Test that the url refers to Sonar. '''
        self.assertEqual(dict(Sonar=FakeSonar().url()), self.__metric.url())

    def test_report(self):
        ''' Test that the report is correct. '''
        self.assertEqual('Het totaal aantal LOC voor alle producten is '
                         '123 regels code.', self.__metric.report())

    def test_recent_history(self):
        ''' Test that the recent history subtracts the minimum value of
            each value so that more data can be plotted. '''
        self.assertEqual([0, 100], self.__metric.recent_history())

    def test_should_be_measured(self):
        ''' Test that the metric should be measured if the project
            requires it. '''
        project = domain.Project(
            requirements=[requirement.TRUSTED_PRODUCT_MAINTAINABILITY])
        self.assertTrue(metric.TotalLOC.should_be_measured(project))

    def test_should_not_be_measured(self):
        ''' Test that the metric should not be measured by default. '''
        self.assertFalse(metric.TotalLOC.should_be_measured(domain.Project()))
