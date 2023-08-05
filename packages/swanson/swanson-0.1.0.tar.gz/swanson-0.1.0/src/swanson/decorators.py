import functools
import re

from swanson.handlers import Matcher, StepHandler

def step(pattern, clause=None):
    def create_handler(func_or_handler):
        if isinstance(func_or_handler, StepHandler):
            return StepHandler(matchers=(matcher,) + func_or_handler.matchers, func=func_or_handler.func)
        else:
            return StepHandler(matchers=(matcher,), func=func_or_handler)

    matcher = Matcher(regex=re.compile(pattern), clause=clause)
    return create_handler

given = functools.partial(step, clause='given')
when = functools.partial(step, clause='when')
then = functools.partial(step, clause='then')
