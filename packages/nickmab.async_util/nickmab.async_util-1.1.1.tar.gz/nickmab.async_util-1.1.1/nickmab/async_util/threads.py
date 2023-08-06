__author__ = 'nickmab'

import types
import threadpool
from threading import Thread, Lock
from Queue import Queue
from . import _utils
from _utils import validate_type as _validate_type
from _utils import is_coroutine as _is_coroutine

"""Contains convenience classes for working with basic ThreadPools and similar basic tasks."""

class FuncWrap:
    """Class that wraps a func call, including args, kwargs, result or exceptions.

    Useful in conjunction with a basic ThreadPool (for example) if you do not wish to bother
    separately implementing a separate callback for handing results and exceptions.

    That said, you can define a callback to handle the results the function returns. The callback is
    called with a lock on the thread that the FuncWrap is instantiated in, so the call (and mutating
    objects in the same thread within the callback is safe.

    Attributes:
        target (func): The function to be called. This is the only thing guaranteed to 
            have a True truth value no matter what (i.e. nothing else is required).
        name (str): You can name this FuncWrap instance for future reference.
        args (tuple): The arguments to be provided to the target func when called.
        kwargs (dict): Keyword arguments to be provided to your target func when called.
        callback (func): Function to be called with this FuncWrap instance as its sole
            argument when the target function returns (or raises an exception).
        result (object): Whatever your function returned (presuming run has been called),
            which could also be None.
        exception (Exception): If an exception was raised during your function's execution,
            it will be here (or None if not).

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

        As an alternative, we could have defined a callback to handle the results::

            def get_results(fw):
                if fw.exception:
                    raise fw.exception
                else:
                    print 'the result is %s' %fw.result
            
            fw = FuncWrap(target=f, name='example', args=(2, 3), 
                kwargs={ 'c': 4, 'd': 5 }, callback=get_results)
            fw.run()

    """
    def __init__(self, target=None, name='', args=(), kwargs={}, callback=None):
        """init with target function and optional name, args, kwargs and 'OnFinished' callback function.

        The target function is the only required argument here (i.e. you do not have to name it and of course
        your function might not need any arguments at all).

        If a callback is provided, it gets called with a lock on the same thread that the FuncWrap was 
        instantiated in.

        Args:
            target (func): The function to be called.
            name (str, optional): You can name this FuncWrap instance for future reference.
            args (tuple, optional): The arguments to be provided to the target func when called.
            kwargs (dict, optional): Keyword arguments to be provided to your target func when called.
            callback (func, optional): Call this function with this FuncWrap as its sole argument when the 
                target function returns (either with a result or exception).

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
        if callback:
            _validate_type('callback', callback, types.FunctionType)

        self._lock = Lock()
        self.target = target 
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.callback = callback
        self.result = None
        self.exception = None

    def run(self):
        """Call target func with args + kwargs in a try/except, store the result (or exception) and call callback func."""
        try:
            self.result = self.target(*self.args, **self.kwargs)
        except Exception as e:
            self.exception = e

        if self.callback:
            with self._lock:
                self.callback(self)
        

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


class ThreadFunnel:
    """Lets 'n' producer generators send objects to 1 consumer coroutine, each running in their own thread.

    It only makes sense to use this if the length (latency) of the work done is large relative to the
    frequency with which objects need to be shared across the thread boundary (i.e. there is a fair amount of
    overhead in this that comes from safely passing objects between the producers and consumer and 
    handling exceptions in worker threads.

    Example:
        Suppose we want to produce and collate data from 3 different sources and use it to produce
        a single unified output. For example, we might have 3 (rather long) text files that we want to scan
        for some pattern, extract some key information, collect it together and do some post-processing. 

        Let's imagine we have some log files produced by some kind of server and we want to count the number
        of times a certain user has logged in (and do other stuff). 

        We might have a producer that looks like this::
        
            import re
            
            my_pattern = re.compile(r'(.*?) UserLogin user\(([^)]*)\) data\(([^)]*)\).*')
            def data_gen(filename):
                with open(filename, 'rb') as f:
                    for line in f:
                        m = my_pattern.match(line):
                        if m:
                            yield m

        Now let's say we have a 'consumer' that looks like this::

            # since the coroutine only gets sent data once at a time from one single thread,
            # this is threadsafe. 
            user_login_count = {}
            def count_user_logins():
                while True:
                    m = yield
                    username = m.group(2)
                    if username not in user_login_count:
                        user_login_count[username] = 0
                    user_login_count[username] += 1

        We can now run this concurrently for an arbitrary number of input files::

            logs = ['log_1.txt', 'log_2.txt', 'log_3.txt']
            gens = [data_gen(log) for log in logs]
            funnel = ThreadFunnel(gens, count_user_logins)
            funnel.run()

        That's it. 

    """
    def __init__(self, producers=[], consumer=None, trust_coroutine_impl=False):
        """Init with a list of generators to send to a coroutine

        Args:
            producers (list): A list of generators that produce objects to send to the consumer coroutine.
            consumer (function):  Must be a function that will return a coroutine 
                when called. The function must take no arguments. The coroutine must handle all inputs 
                from the yield keyword, must also yield no outputs at all, and must not return / exit.
                Exception handling is not strictly necessary, though, as the ThreadFunnel will catch them.
            trust_coroutine_impl (bool, optional): False by default. Set this to True if you know
                that a call to inspect.getsourcelines(consumer_coroutine) will fail to find the source code
                for your coroutine (e.g. if you're running this in an interactive shell) and so will
                not be able to accurately validate it.

        Raises:
            TypeError: Throws if the args are not the right type.
            ValueError: Throws if non-optional args are not provided

        """
        # validation first
        if not producers or not consumer:
            raise ValueError('Must provide a list of producer generators and a coroutine consumer function.')
        _validate_type('producers', producers, types.ListType)
        _validate_type('consumer', consumer, types.FunctionType)
        _validate_type('trust_coroutine_impl', trust_coroutine_impl, types.BooleanType)
        for prod in producers:
            _validate_type('producer_instance', prod, types.GeneratorType)
        if not trust_coroutine_impl and not _is_coroutine(consumer):
            raise ValueError('Consumer coroutine %s code is invalid. ' %consumer.__name__ +
                'yield keyword must only ever appear alone on a line (to drop sent input) ' + 
                'or to the rhs of an assignment operator.')    
            
        self.producers = producers
        self.consumer = consumer

    def run(self):
        """Start all producer and consumer threads and wait (block) til all have returned.

        If an exception is encountered in any of the producers or the consumer, we will catch it 
        and exit early.

        Raises:
            ProducerException: Raised if there is an exception caught in a producer generator.
            ConsumerException: Raised if there is an exception caught in the consumer coroutine.

        """
        class ProducerException(Exception):
            def __init__(self, gen, caught_exception):
                message = 'Encountered an exception in worker thread of generator \'%s\'' %gen.__name__
                super(Exception, self).__init__(message)
                self.caught_exception = caught_exception

        class ConsumerException(Exception):
            def __init__(self, coroutine, caught_exception):
                message = 'Encountered an exception in worker thread of coroutine \'%s\'' %coroutine.__name__
                super(Exception, self).__init__(message)
                self.caught_exception = caught_exception

        # first let's define a worker func that knows how to run these generators
        def _gen_worker(gen, out_q):
            try:
                while True:
                    out_q.put(gen.next())
            except Exception as e:
                if not isinstance(e, StopIteration):
                    raise ProducerException(gen, e)
                    
        # now the function to consume the output of the generators
        def _cons_worker(cons, in_q):
            while True:
                obj = in_q.get()
                try:
                    cons.send(obj)
                    in_q.task_done()
                except Exception as e:
                    raise ConsumerException(cons, e)
             
        # the work_q is the one that the producers and consumer use to share input/output objects
        work_q = Queue()
        # the wait_finish_q is what we will use to exit early if there's an exception in our work threads
        wait_finish_q = Queue()
        # this is where we'll store the exception if we catch one in a worker thread
        bad_func_wrap = []
        # this gets called a) when a generator finishes or b) when there's an exception in the workers.
        def _func_wrap_callback(func_wrap):
            if func_wrap.exception:
                bad_func_wrap.append(func_wrap)
                while not wait_finish_q.empty():
                    wait_finish_q.get()
                    wait_finish_q.task_done()
            else:
                if wait_finish_q.qsize() > 1:
                    wait_finish_q.get()
                    wait_finish_q.task_done()
                else:
                    work_q.join()
                    wait_finish_q.get()
                    wait_finish_q.task_done()

        func_wraps = []
        for prod in self.producers:
            func_wraps.append(FuncWrap(target=_gen_worker, args=(prod, work_q), callback=_func_wrap_callback))
            # the wait_finish_q is effectively just a count of outstanding producers
            wait_finish_q.put(1)
        
        cons = self.consumer()
        cons.next()
        func_wraps.append(FuncWrap(target=_cons_worker, args=(cons, work_q), callback=_func_wrap_callback))
        
        pool = FuncWrapPool(len(func_wraps), func_wraps)
        pool_thr = Thread(target=pool.run, args=())
        pool_thr.daemon = True
        pool_thr.start()
        
        wait_finish_q.join()
        if bad_func_wrap:
            raise bad_func_wrap[0].exception
