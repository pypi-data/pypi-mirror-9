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


from ..metric_source_mixin import SonarDashboardMetricMixin
from ..quality_attributes import DEPENDENCY_QUALITY
from ...domain import LowerIsBetterMetric, LowerPercentageIsBetterMetric
from ...formatting import HTMLFormatter
from ... import utils, metric_source


class CyclicDependencies(SonarDashboardMetricMixin, LowerIsBetterMetric):
    # pylint: disable=too-many-public-methods
    ''' Return the number of cyclic dependencies between packages. '''

    name = 'Cyclische afhankelijkheden'
    norm_template = 'Maximaal {target} cyclische afhankelijkheden tussen ' \
        'packages. Meer dan 10 is rood.'
    template = '{name} heeft {value} cyclische afhankelijkheden.'
    target_value = 0
    low_target_value = 10
    quality_attribute = DEPENDENCY_QUALITY

    def value(self):
        return self._sonar.package_cycles(self._sonar_id())


class SnapshotDependencies(LowerIsBetterMetric):
    # pylint: disable=too-many-public-methods
    ''' Metric for measuring the number of the dependencies on snapshot versions
        of other products. '''
    name = 'Snapshot afhankelijkheden'
    norm_template = 'Maximaal {target} afhankelijkheden op snapshot ' \
        'versies van andere producten. Meer dan {low_target} is rood.'
    template = '{name} heeft {value} afhankelijkheden op snapshot ' \
        'versies van andere producten.'
    target_value = 0
    low_target_value = 2
    quality_attribute = DEPENDENCY_QUALITY
    metric_source_classes = (metric_source.VersionControlSystem,
                             metric_source.Pom)

    @classmethod
    def can_be_measured(cls, product, project):
        return super(SnapshotDependencies, cls).can_be_measured(product,
                                                              project) and \
            product.product_version()  # Only report for released versions

    def __init__(self, *args, **kwargs):
        self.__report = kwargs.pop('report')
        super(SnapshotDependencies, self).__init__(*args, **kwargs)

    def value(self):
        return len(self.__snapshot_dependencies())

    def url(self):
        # pylint: disable=star-args
        urls = dict()
        for dependency in self.__snapshot_dependencies():
            product = self.__report.get_product(*dependency)
            label = '{}:{}'.format(dependency[0], dependency[1] or 'trunk')
            urls[label] = HTMLFormatter.product_url(product)
        return urls
 
    def __snapshot_dependencies(self):
        ''' Return a list of snapshot dependencies of this product. '''
        return [dependency for dependency in self._subject.dependencies() if \
                not dependency[1]]


class DependencyQuality(LowerPercentageIsBetterMetric):
    # pylint: disable=too-many-public-methods
    ''' Metric for measuring the quality of the dependencies of the project. '''

    name = 'Kwaliteit van afhankelijkheden'
    norm_template = 'Maximaal {target}% van de afhankelijkheden tussen ' \
        'componenten is naar componenten die "rode" metrieken hebben. ' \
        'Meer dan {low_target}% is rood.'
    template = '{value:.0f}% van de afhankelijkheden ({nr_not_ok_deps} van ' \
        'de {nr_deps}) is naar componenten die "rode" metrieken hebben.'
    target_value = 10
    low_target_value = 20
    quality_attribute = DEPENDENCY_QUALITY
    metric_source_classes = (metric_source.Pom,
                             metric_source.VersionControlSystem)

    def __init__(self, *args, **kwargs):
        self.__report = kwargs.pop('report')
        super(DependencyQuality, self).__init__(*args, **kwargs)

    def _numerator(self):
        return self.__dependency_colors().count('red')

    def _denominator(self):
        return len(self.__dependency_colors())

    @utils.memoized
    def __dependency_colors(self):
        ''' Return the colors of all dependencies in the project. '''
        # pylint: disable=star-args
        colors = []
        for product in self.__report.products():
            for dependency in product.dependencies(recursive=False):
                product = self.__report.get_product(*dependency)
                color = self.__report.get_product_section(product).color()
                colors.append(color)
        return colors

    def url_label(self):
        return 'Componenten die "rode" metrieken hebben'

    def url(self):
        # pylint: disable=star-args
        urls = dict()
        for product in self.__report.products():
            for dependency in product.dependencies(recursive=False):
                product = self.__report.get_product(*dependency)
                label = '{}:{}'.format(dependency[0], dependency[1] or 'trunk')
                urls[label] = HTMLFormatter.product_url(product)
        return urls

    def _parameters(self):
        # pylint: disable=protected-access
        parameters = super(DependencyQuality, self)._parameters()
        parameters['nr_not_ok_deps'] = self._numerator()
        parameters['nr_deps'] = self._denominator()
        return parameters
