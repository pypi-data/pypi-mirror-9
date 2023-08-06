__author__ = 'nickmab'

import types
import threadpool
from . import _utils
from _utils import validate_type as _validate_type

"""Contains convenience classes for working with basic ThreadPools and similar basic tasks."""

class FuncWrap:
    """Class that wraps a func call, including args, kwargs, result or exceptions.

    Useful in conjunction with a basic ThreadPool (for example) if you do not wish to bother
    separately implementing a separate callback for handing results and exceptions.

    Attributes:
        target (func): The function to be called. This is the only thing guaranteed to 
            have a True truth value no matter what (i.e. nothing else is required).
        name (str): You can name this FuncWrap instance for future reference.
        args (tuple): The arguments to be provided to the target func when called.
        kwargs (dict): Keyword arguments to be provided to your target func when called.
        result (object): Whatever your function returned (presuming run has been called),
            which could also be None.
        exception (Exception): If an exception was raised during your function's execution,
            it will be here (or None if not).

    Args:
        target (func): The function to be called.
        name (str, optional): You can name this FuncWrap instance for future reference.
        args (tuple, optional): The arguments to be provided to the target func when called.
        kwargs (dict, optional): Keyword arguments to be provided to your target func when called.
    
    Example:
        
        Imagine we have a simple function that we want to run in a separate thread::

            def f(a, b, c=None, d=1):
                x = a + b
                if x:
                    x += c
                return x * d

        We can run this function and capture the results for future reference as follows::

            fw = FuncWrap(target=f, name='example', args=(2, 3), kwargs={ 'c': 4, 'd': 5 })
            fw.run()

        We can subsequently find out what happened::

            # in this case there is no exception, but if there was it would be here...
            if fw.exception:
                # in real life you might not just throw it again, but this is just an example...
                raise fw.exception
            else:
                # the return value will be (2 + 3 + 4) * 5 == 45
                print 'the result is %s' %fw.result

    """
    def __init__(self, target=None, name='', args=(), kwargs={}):
        """init with target function, optional name, args and kwargs to identify and call that function.

        The target function is the only required argument here (i.e. you do not have to name it and of course
        your function might not need any arguments at all).

        Args:
            target (func): The function to be called.
            name (str, optional): You can name this FuncWrap instance for future reference.
            args (tuple, optional): The arguments to be provided to the target func when called.
            kwargs (dict, optional): Keyword arguments to be provided to your target func when called.

        Raises:
            ValueError: If no target function is provided.
            TypeError: If any of the arguments provided are not the correct type.

        """
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
        """Call target func with args and kwargs in a try/except and store the result (or exception)."""
        try:
            self.result = self.target(*self.args, **self.kwargs)
        except Exception as e:
            self.exception = e
        

class FuncWrapPool:
    """Runs a collection of FuncWrap instances using workers in a threadpool.ThreadPool.

    Attributes:
        func_wraps (list): This contains the list of FuncWrap instances whose targets are 
            called by worker functions in a ThreadPool. Inspect this list of FuncWraps after
            the results have all returned to get the results and/or exceptions.

    Example:
        Imagine we want to run two long-running functions at ond safely capture results::

            def f(a, b):
                return a + b

            def g(s='hello'):
                return s.count('h')

        We can package these as FuncWraps as follows (in real life you might have a
        long list of different arguments to call these functions for):: 

            # Any iterable will do; we will use a list and just construct these manually inline.
            fws = [FuncWrap(target=f, args=(2, 3)), FuncWrap(target=g, kwargs={ 's': 123 })]

        We can now put these in a FuncWrapPool and run them asynchronously. Note that the second 
        of these FuncWraps will obviously result in an AttributeError:

            fwp = FuncWrapPool(2, fws)
            # a call to run() will block until all results are in
            fwp.run()

        So the FuncWrap instances in our "fws" list (above) will now be populated with results/exceptions::

            res1 = fws[0].result # this will be 2 + 3 == 5 and the exception will be None
            raise fws[1].exception # the exception will be here, the result will be None. 

    """
    def __init__(self, num_workers=5, func_wrap_instances_iterable=[]):
        """Init with a number of worker threads and an iterable of FuncWrap instances to run later.

        Args:
            num_workers (int, optional): The (default 5) number of workers to put in our threadpool.ThreadPool.
            func_wrap_instances_iterable (object): Must be an iterable that yields references (using 
                standard for _ in iter_obj: syntax) to FuncWrap instances for this FuncWrapPool instance
                to run in workers in a threadpool.ThreadPool.

        Raises:
            TypeError: Throws if the func_wrap_instances_iterable argument is not iterable! Also throws
                if num_workers is not an int.
            ValueError: Although it is a kwarg, the default empty list for the func_wrap_instances_iterable
                argument is not acceptable and this will throw a ValueError if it is not provided.

        """
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
        """Run all FuncWraps in a threadpool.ThreadPool and wait (block) til all have returned."""
        pool = threadpool.ThreadPool(self.num_workers)
        [pool.putRequest(threadpool.WorkRequest(fw.run)) for fw in self.func_wraps]
        pool.wait()
