import collections
import os
import os.path

from django.test import TestCase, runner

from swanson.data import Feature
from swanson.exceptions import UnimplementedScenariosError
from swanson.signals import pre_scenario_test

class UnimplementedBDDTestCase(TestCase):
    def __init__(self, methodName='test_unimplemented_feature', runner=None):
        self.runner = runner
        return super(UnimplementedBDDTestCase, self).__init__(methodName)

    def test_unimplemented_feature(self):
        if not self.runner:
            raise Exception('Test runner not set')

        unimplemented = collections.defaultdict(list)
        for feature_filename in self.iter_feature_filenames('.'):
            feature_filename = os.path.abspath(feature_filename)
            feature = Feature.from_filename(feature_filename)

            for scenario in feature.scenarios:
                if scenario.title not in self.runner.implemented_scenarios[feature_filename]:
                    unimplemented[feature_filename].append(scenario.title)

        if unimplemented:
            raise UnimplementedScenariosError('\n{}'.format('\n'.join(
                ' * {}\n{}'.format(
                    os.path.relpath(feature_filename),
                    '\n'.join(
                        '   * {}'.format(scenario_title)
                        for scenario_title in scenario_titles
                    )
                )
                for feature_filename, scenario_titles in sorted(unimplemented.iteritems())
            )))

    def iter_feature_filenames(self, path):
        for path, _, basenames in os.walk(path):
            for basename in basenames:
                if basename.endswith('.feature'):
                    yield os.path.join(path, basename)

class TestRunnerMixin(object):
    def __init__(self, *args, **kwargs):
        super(TestRunnerMixin, self).__init__(*args, **kwargs)
        pre_scenario_test.connect(self.pre_scenario_test)

    def pre_scenario_test(self, feature_filename, scenario_title, **kwargs):
        self.implemented_scenarios[feature_filename].add(scenario_title)

    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        self.implemented_scenarios = collections.defaultdict(set)
        return super(TestRunnerMixin, self).run_tests(test_labels, extra_tests, **kwargs)

    def build_suite(self, test_labels=None, extra_tests=None, **kwargs):
        suite = super(TestRunnerMixin, self).build_suite(test_labels, extra_tests, **kwargs)
        if not test_labels:
            suite.addTest(UnimplementedBDDTestCase(runner=self))
        return suite

class DiscoverRunner(TestRunnerMixin, runner.DiscoverRunner):
    pass
