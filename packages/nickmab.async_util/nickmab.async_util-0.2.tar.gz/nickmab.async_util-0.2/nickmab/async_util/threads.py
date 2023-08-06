__author__ = 'nickmab'

import types
import threadpool
from . import _utils
from _utils import validate_type as _validate_type

'''Contains convenience classes for working with basic ThreadPools and similar basic tasks.'''

class FuncWrap:
    '''Class for wrapping a function call, including remembering
    its args, return value (or exception) and optionally naming it. Useful in conjunction
    with basic ThreadPools where you do not wish to implement
    a callback function to handle new results.'''
    def __init__(self, target=None, name='', args=(), kwargs={}):
        '''takes a target func, args (tup) and kwargs (dict) for that func and 
        optional name (str) (for identification) to run later by calling FuncWrap.run'''
        # validation first
        if not target:
            raise ValueError('Must provide a valid target function at a minimum.')
        _validate_type('target', target, types.FunctionType)
        _validate_type('name', name, types.StringType)
        _validate_type('args', args, types.TupleType)
        _validate_type('kwargs', kwargs, types.DictionaryType)

        self.target = target 
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.result = None
        self.exception = None

    def run(self):
        '''call the target function with the specified args / kwargs within a 
        try/except and store the result (or exception).'''
        try:
            self.result = self.target(*self.args, **self.kwargs)
        except Exception as e:
            self.exception = e
        

class FuncWrapPool:
    '''Class for creating a ThreadPool with a specified number of workers and 
    running through an iterable of FuncWrap instances conveniently.'''
    def __init__(self, num_workers=5, func_wrap_instances_iterable=[]):
        '''Specify a number of worker threads and provide an iterable of FuncWrap instances'''
        # validation and logic inline
        if not func_wrap_instances_iterable:
            raise ValueError('Must provide a non-empty iterable with FuncWrap instances!')
        _validate_type('num_workers', num_workers, types.IntType)
        self.num_workers = num_workers
        self.func_wraps = []
        for fw in func_wrap_instances_iterable:
            try:
                _validate_type('func_wrap', fw, FuncWrap)
            except TypeError as e:
                raise TypeError('FuncWrapPool expects an iterable of FuncWrap instances. ' +
                    'Instead got %s as part of %s.' %(fw, func_wrap_instances_iterable))
            self.func_wraps.append(fw)
        
    def run(self):
        '''start a ThreadPool with (self.num_workers) workers, run all our FuncWrap instances
        and wait for the results to all come in.'''
        pool = threadpool.ThreadPool(self.num_workers)
        [pool.putRequest(threadpool.WorkRequest(fw.run)) for fw in self.func_wraps]
        pool.wait()
