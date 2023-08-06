__author__ = 'nickmab'

import types
import inspect

'''Utility code for use by other py files within this package.'''

def validate_type(obj_name, obj, desired_type):
    if not isinstance(obj, desired_type):
        raise TypeError('%s must be a %s. Instead got %s: %s.'
            %(obj_name, desired_type.__name__, type(obj).__name__), obj)

def is_coroutine(obj):
    if not isinstance(obj, types.FunctionType):
        return False
    try:
        yields = filter(lambda l: 'yield' in l, inspect.getsourcelines(obj)[0])
    except IOError:
        # indicates could not get source code for the object.
        return None
    return all('=' in l or l.strip() == 'yield' for l in yields)
