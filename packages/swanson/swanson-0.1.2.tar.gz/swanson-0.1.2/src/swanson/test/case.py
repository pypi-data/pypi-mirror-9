import os.path
import re
import sys

import six
from django import test

from swanson.data import Feature
from swanson.exceptions import StepError
from swanson.handlers import StepHandler, StepHandlers
from swanson.signals import pre_scenario_test

class TestCaseMixin(object):
    def run_scenario(self, title):
        pre_scenario_test.send(
            sender=self,
            feature_filename=self.get_feature_filename(),
            scenario_title=title
        )

        step_handlers = self.get_step_handlers()
        for scenario in self.get_scenario(title).expand_examples():
            for step in scenario.steps:
                try:
                    handler_match = step_handlers.get_handler_match_for_step(step)
                    handler_match.handler.func(self, step, *handler_match.match.groups())
                except Exception as exc:
                    new_exc = StepError('Error running {!r} on line {} of {}:\n\n{}: {}'.format(
                        str(step),
                        step.index + 1,
                        os.path.relpath(step.scenario.feature.filename),
                        type(exc).__name__,
                        exc
                    ))
                    six.reraise(type(new_exc), new_exc, sys.exc_info()[2])

    def get_scenario(self, title):
        feature = self.get_feature()
        
        matching_scenarios = [
            scenario
            for scenario in feature.scenarios
            if scenario.title == title
        ]

        if len(matching_scenarios) == 0:
            raise Exception('No scenarios named {!r}'.format(title))
        elif len(matching_scenarios) > 1:
            raise Exception('Multiple scenarios named {!r}'.format(title))
        else:
            return matching_scenarios[0]

    def get_feature(self):
        return Feature.from_filename(self.get_feature_filename())

    def get_feature_filename(self):
        filename = sys.modules[self.__module__].__file__
        return os.path.join(
            os.path.dirname(filename),
            re.sub(r'^test_', '',
                re.sub(r'\.[^.]+$', '.feature', os.path.basename(filename))
            )
        )

    def get_step_handlers(self):
        step_handlers = []
        for name in dir(self):
            value = getattr(self, name)
            if isinstance(value, StepHandler):
                step_handlers.append(value)

        return StepHandlers(step_handlers)

class SimpleTestCase(TestCaseMixin, test.SimpleTestCase):
    pass

class TransactionTestCase(TestCaseMixin, test.TransactionTestCase):
    pass

class TestCase(TestCaseMixin, test.TestCase):
    pass

class LiveServerTestCase(TestCaseMixin, test.LiveServerTestCase):
    pass
