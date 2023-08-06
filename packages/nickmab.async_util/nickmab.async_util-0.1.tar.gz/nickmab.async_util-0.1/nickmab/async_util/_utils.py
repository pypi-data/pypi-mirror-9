__author__ = 'nickmab'

'''Utility code for use by other py files within this package.'''

def validate_type(obj_name, obj, desired_type):
    if not isinstance(obj, desired_type):
        raise TypeError('%s must be a %s. Instead got %s: %s.'
            %(obj_name, desired_type.__name__, type(obj).__name__), obj)
