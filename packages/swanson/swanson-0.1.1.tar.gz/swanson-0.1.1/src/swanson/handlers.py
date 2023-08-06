import collections

from swanson.exceptions import MultipleStepHandlers, NoStepHandlers

StepHandler = collections.namedtuple('StepHandler', ('matchers', 'func'))
Matcher = collections.namedtuple('StepHandler', ('regex', 'clause'))

HandlerMatch = collections.namedtuple('HandlerMatch', ('handler', 'matcher', 'match'))

class StepHandlers(object):
    def __init__(self, handlers):
        self._handlers = handlers

    def get_handler_match_for_step(self, step):
        handler_matches = []
        for handler in self._handlers:
            for matcher in handler.matchers:
                if matcher.clause is None or matcher.clause == step.clause:
                    match = matcher.regex.search(step.title)
                    if match:
                        handler_matches.append(HandlerMatch(handler, matcher, match))
                        # Continue to the next handler.
                        break

        if not handler_matches:
            raise NoStepHandlers('No step handlers found for {!r}'.format(
                str(step)
            ))

        if len(handler_matches) > 1:
            raise MultipleStepHandlers('Multiple step handlers found for {!r}\n{}'.format(str(step), '\n'.join(
                ' * {}({!r})'.format(handler_match.matcher.clause or 'step', handler_match.matcher.regex.pattern)
                for handler_match in handler_matches
            )))

        return handler_matches[0]
