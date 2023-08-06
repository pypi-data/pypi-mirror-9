import copy
import re

import gherkin_parser
import six

class Feature(object):
    def __init__(self, parsed, filename='<unknown>'):
        def scenario_cls(parsed_scenario):
            if parsed_scenario['title']['is_outline']:
                return ScenarioOutline
            else:
                return Scenario

        self.filename = filename
        self.tags = parsed['tags']['content'] if parsed['tags'] else None
        self.title = parsed['title']['content']
        self.description = parsed['description']['content'] if parsed['description'] else None
        self.background = Background(self, parsed['background']) if parsed['background'] else None
        self.scenarios = [
            scenario_cls(parsed_scenario)(self, parsed_scenario)
            for parsed_scenario in parsed['scenarios']
        ]

    @classmethod
    def from_filename(cls, filename):
        parsed = gherkin_parser.parse_from_filename(filename)
        return cls(parsed, filename)

    @classmethod
    def from_string(cls, string):
        parsed = gherkin_parser.parse_lines(string.split('\n'))
        return cls(parsed)

class Background(object):
    def __init__(self, feature, parsed):
        self.feature = feature

        self.title = parsed['title']['content']
        self.description = parsed['description']['content'] if parsed['description'] else None
        self.steps = [
            Step(self, parsed_step)
            for parsed_step in parsed['steps']
        ]

class BaseScenario(object):
    def __init__(self, feature, parsed):
        self.feature = feature

        self.tags = parsed['tags']['content'] if parsed['tags'] else None
        self.title = parsed['title']['content']
        self.description = parsed['description']['content'] if parsed['description'] else None
        self.steps = [
            Step(self, parsed_step)
            for parsed_step in parsed['steps']
        ]

class Scenario(BaseScenario):
    def __init__(self, feature, parsed):
        super(Scenario, self).__init__(feature, parsed)
        self.examples = None

    def expand_examples(self):
        return [self]

class ScenarioOutline(BaseScenario):
    def __init__(self, feature, parsed):
        super(ScenarioOutline, self).__init__(feature, parsed)
        self.examples = ScenarioExamples(parsed['examples'])

    def expand_examples(self):
        return [
            self.for_example(example)
            for example in self.examples.table.dicts
        ]

    def for_example(self, example):
        def replacement(match):
            return example[match.group(1).lower()]

        example = {
            key.lower(): value
            for (key, value) in six.iteritems(example)
        }

        regex = re.compile(r'(?i)<({})>'.format('|'.join(
            re.escape(key)
            for key in six.iterkeys(example)
        )))

        scenario = copy.deepcopy(self)
        for step in scenario.steps:
            step.title = regex.sub(replacement, step.title)
            step.text = regex.sub(replacement, step.text) if step.text else None

        return scenario

class ScenarioExamples(object):
    def __init__(self, parsed):
        self.title = parsed['title']
        self.table = Table(parsed['table'])

class Step(object):
    def __init__(self, scenario, parsed):
        self.scenario = scenario

        self.index = parsed['title']['index']
        self.clause = parsed['title']['clause']
        self.title = parsed['title']['content']
        self.text = parsed['text']['content'] if parsed['text'] else None
        self.table = Table(parsed['table']) if parsed['table'] else None

    def __str__(self):
        return '{} {}'.format(self.clause.title(), self.title)

class Table(object):
    def __init__(self, parsed):
        self._rows = [
            row['columns']
            for row in parsed
        ]

    def __len__(self):
        return len(self._rows)

    def __iter__(self):
        return iter(self._rows)

    @property
    def header(self):
        return self._rows[0]

    @property
    def dicts(self):
        return [
            dict(six.moves.zip_longest(self.header, row[:len(self.header)]))
            for row in self._rows[1:]
        ]
