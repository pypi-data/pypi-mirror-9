__author__ = 'nickmab'

import types
import inspect

'''Utility code for use by other py files within this package.'''

def validate_type(obj_name, obj, desired_type):
    if not isinstance(obj, desired_type):
        raise TypeError('%s must be a %s. Instead got %s: %s.'
            %(obj_name, desired_type.__name__, type(obj).__name__, obj))

def is_coroutine(obj):
    if not isinstance(obj, types.FunctionType):
        return False
    try:
        yields = filter(lambda l: 'yield' in l, inspect.getsourcelines(obj)[0])
        if not yields:
            return False
    except IOError:
        # indicates could not get source code for the object.
        return None
    for line in yields:
        if '=' not in line:
            # must be used like "x = yield" and a yield on its own is considered invalid.
            return False
        if 'yield' in line.split('=')[0]:
            # catch edge cases like "yield x == y"
            return False
    return True
