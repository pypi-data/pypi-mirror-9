import collections
import re

import pydentifier
import six

class InvalidParameters(Exception):
    pass

class DuplicateScenarioTitles(Exception):
    pass

class CodeGen(object):
    InvalidParameters = InvalidParameters
    DuplicateScenarioTitles = DuplicateScenarioTitles

    @classmethod
    def generate_test_module(cls, feature):
        return '{}\n'.format(
            '\n\n'.join(filter(None, (
                cls.generate_test_module_header(feature),
                cls.generate_test_case(feature)
            )))
        )

    @classmethod
    def generate_test_module_header(cls, feature):
        return 'from swanson import TestCase, step, given, when, then'

    @classmethod
    def generate_test_case(cls, feature):
        member_identifiers = UniqueIdentifiers()

        return 'class {}({}):\n{}'.format(
            cls.get_test_case_name(feature),
            cls.get_parent_test_case_name(feature),
            cls.indent(
                cls.generate_test_case_body(feature, member_identifiers)
            )
        )

    @classmethod
    def get_test_case_name(cls, feature):
        return pydentifier.upper_camel(feature.title, 'BDD', 'TestCase')

    @classmethod
    def get_parent_test_case_name(cls, feature):
        return 'TestCase'

    @classmethod
    def generate_test_case_body(cls, feature, member_identifiers=None):
        return '\n\n'.join(filter(None, (
            cls.generate_test_case_docstring(feature),
            cls.generate_test_case_functions(feature, member_identifiers),
            cls.generate_feature_step_handlers(feature, member_identifiers)
        ))) or 'pass'

    @classmethod
    def generate_test_case_docstring(cls, feature):
        return '"""\n{}\n"""'.format(feature.title)

    @classmethod
    def generate_test_case_functions(cls, feature, member_identifiers=None):
        if member_identifiers is None:
            member_identifiers = UniqueIdentifiers()

        seen_scenario_titles = set()

        functions = []
        for scenario in feature.scenarios:
            if scenario.title not in seen_scenario_titles:
                seen_scenario_titles.add(scenario.title)
            else:
                raise DuplicateScenarioTitles(
                    'Multiple scenarios named {!r}'.format(
                        scenario.title
                    )
                )

            function_name = member_identifiers.get(
                cls.get_test_case_function_name(scenario)
            )

            functions.append(
                cls.generate_test_case_function(scenario, function_name)
            )

        return '\n\n'.join(functions)

    @classmethod
    def get_test_case_function_name(cls, scenario):
        return pydentifier.lower_underscore(scenario.title, prefix='test')

    @classmethod
    def generate_test_case_function(cls, scenario, function_name):
        return cls.generate_function(
            function_name,
            ('self',),
            cls.get_test_case_function_body(scenario)
        )

    @classmethod
    def get_test_case_function_body(cls, scenario):
        return '"""\n{}\n"""\n\nself.run_scenario({!r})'.format(
            scenario.title,
            scenario.title
        )

    @classmethod
    def generate_feature_step_handlers(cls, feature, member_identifiers=None):
        return cls.generate_step_handlers(
            cls.iter_feature_steps(feature),
            member_identifiers
        )

    @classmethod
    def iter_feature_steps(cls, feature):
        if feature.background:
            for step in feature.background.steps:
                yield step

        for scenario in feature.scenarios:
            for expanded in scenario.expand_examples():
                for step in expanded.steps:
                    yield step

    @classmethod
    def generate_step_handlers(cls, steps, member_identifiers=None):
        if member_identifiers is None:
            member_identifiers = UniqueIdentifiers()

        clause_handlers = collections.OrderedDict((
            (clause, collections.OrderedDict())
            for clause in ('given', 'when', 'then')
        ))
        for step in steps:
            if step.title in clause_handlers[step.clause]:
                continue

            function_name = member_identifiers.get(
                cls.get_step_handler_function_name(step)
            )
            
            handler = cls.generate_step_handler(step, function_name)

            clause_handlers[step.clause][step.title] = handler

        return '\n\n'.join(
            handler
            for handlers in six.itervalues(clause_handlers)
            for handler in six.itervalues(handlers)
        )

    @classmethod
    def get_step_handler_function_name(cls, step):
        return pydentifier.lower_underscore(step.title, prefix=step.clause)

    @classmethod
    def generate_step_handler(cls, step, function_name):
        return '\n'.join((
            cls.generate_step_handler_decorator(step),
            cls.generate_step_handler_function(step, function_name)
        ))

    @classmethod
    def generate_step_handler_decorator(cls, step):
        return '@{}({})'.format(
            step.clause,
            cls.generate_step_pattern(step)
        )

    @classmethod
    def generate_step_pattern(cls, step):
        return cls.generate_raw_string(
            cls.get_step_pattern(step)
        )

    @classmethod
    def generate_raw_string(cls, string, quote="'"):
        chars = []
        for char in string:
            if char == quote:
                chars.append('\\{}'.format(quote))
            elif char == '\\':
                chars.append('\\')
            else:
                chars.append(repr(char)[1:-1])

        return 'r{}{}{}'.format(
            quote,
            ''.join(chars),
            quote
        )

    @classmethod
    def generate_step_handler_function(cls, step, name):
        return cls.generate_function(
            name,
            ('self', 'step'),
            cls.generate_step_handler_function_body(step)
        )

    @classmethod
    def generate_step_handler_function_body(cls, step):
        return '"""\n{} {}\n"""\n\nassert False'.format(
            step.clause.title(),
            step.title
        )

    @classmethod
    def get_step_pattern(cls, step):
        return '(?i)^{}$'.format(
            cls.escape_regex(step.title)
        )

    @classmethod
    def escape_regex(cls, string):
        return re.sub(
            '([[\\^$.|?*+()])',
            r'\1',
            string
        )

    @classmethod
    def generate_function(cls, name, params, body):
        return 'def {}({}):\n{}'.format(
            pydentifier.require_valid(name),
            cls.generate_function_params(params),
            cls.indent(body)
        )

    @classmethod
    def generate_function_params(cls, params):
        seen_params = set()
        for param in params:
            if param in seen_params:
                raise InvalidParameters(
                    'Duplicate parameter {!r}'.format(param)
                )
            seen_params.add(pydentifier.require_valid(param))

        return ', '.join(params)

    @classmethod
    def indent(cls, text):
        return '\n'.join(
            '    {}'.format(line)
            for line in text.split('\n')
        )

class UniqueIdentifiers(set):
    def get(self, name):
        base_name = name
        index = 1
        while name in self:
            index += 1
            name = '{}_{}'.format(base_name, index)
        self.add(name)
        return name
