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


from ...domain import LowerPercentageIsBetterMetric
from ..metric_source_mixin import SonarDashboardMetricMixin
from ..quality_attributes import CODE_QUALITY


class Duplication(SonarDashboardMetricMixin, LowerPercentageIsBetterMetric):
    # pylint: disable=too-many-public-methods
    ''' Metric for measuring the percentage of duplicated lines of code. '''

    norm_template = 'Maximaal {target}% gedupliceerde regels code. ' \
        'Meer dan {low_target}% is rood.'
    template = '{name} heeft {value}% ({numerator} op ' \
        '{denominator}) duplicatie.'
    quality_attribute = CODE_QUALITY

    def _numerator(self):
        return self._sonar.duplicated_lines(self._sonar_id())

    def _denominator(self):
        return self._sonar.lines(self._sonar_id())


class JavaDuplication(Duplication):
    # pylint: disable=too-many-public-methods, too-many-ancestors
    ''' Metric for measuring the percentage of duplicated lines of code in 
        Java code. '''

    name = 'Duplicatie van Java broncode'
    target_value = 0
    low_target_value = 5


class JsfDuplication(Duplication):
    # pylint: disable=too-many-public-methods, too-many-ancestors
    ''' Metric for measuring the percentage of duplicated lines of code in 
        JSF code. '''

    name = 'Duplicatie van JSF broncode'
    target_value = 10
    low_target_value = 20

