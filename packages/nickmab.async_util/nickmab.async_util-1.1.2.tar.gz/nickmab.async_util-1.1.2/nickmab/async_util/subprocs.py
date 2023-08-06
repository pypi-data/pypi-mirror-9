__author__ = 'nickmab'

import types
from . import _utils
from _utils import validate_type as _validate_type
from _utils import is_coroutine as _is_coroutine
import multiprocessing as mp

"""Contains boilerplate code for working with common subprocess-related tasks."""

def generate_and_consume(producer_gen, consumer_func, print_warns=True):
    """Run (and exhaust) a producer generator and consumer function in two separate processes. 

    Given a generator function that produces objects for a handler function to consume,
    set up a pipe between two subprocesses, then send the objects one at a time to
    the consumer function.

    Args:
        producer_gen (generator): Must yield any non-None object to be passed
            through a multiprocessing.Pipe to a handler function.
        consumer_func (function): Must take two arguments. The first is the object
            produced by the producer in the other process and the second is a
            multiprocessing.Queue to which it can optionally put output or results.
        print_warns (bool, optional): True by default. If an exception is caught
            in either the producer or consumer process, a line will be printed to
            stdout specifying this if set to True. Set False to suppress output.

    Returns:
        multiprocessing.Queue: The results produced by the consumer function.

    Raises:
        ValueError: If the producer generator yields a None.
        TypeError: If any of the arguments are invalid types.
        Exception: Any exceptions other than expected StopIteration raised by the two
            child processes will be caught and raised again in the parent process. 

    Example:
        An example of a generator::

            def gen():
                for i in range(10):
                    yield i

        An example of a handler::

            def handle(obj, out_q):
                # do something with the obj...
                out_q.put(2*obj)

        You would use this as follows::

            res = generate_and_consume(gen(), handle)
            tot = 0
            while not res.empty():
                tot += res.get()

        The total would, of course, be 90.

    """
    _validate_type('producer_gen', producer_gen, types.GeneratorType)
    _validate_type('consumer_func', consumer_func, types.FunctionType)
    _validate_type('print_warns', print_warns, types.BooleanType)
    def p_func(conn):
        try:
            while True:
                obj = producer_gen.next()
                if obj is None:
                    raise ValueError('Producer generator %s produced a "None" value! Invalid.' 
                        %producer_gen.__name__)
                conn.send(obj)
        except Exception as e:
            # 'None' sentinel denotes completion
            conn.send(None)
            if not isinstance(e, StopIteration):
                # this indicates there was actually an error, so let's send it through.
                conn.send(e)
            conn.close()
    
    def c_func(conn, lock, out_q, err_q):
        try:
            while True:
                item = conn.recv()
                if item is None:
                    # 'None' sentinel denotes completion, but check whether there was an exception...
                    if conn.poll(0.01):
                        # if there's something more in the queue, it means we've encountered an exception.
                        with lock:
                            if print_warns:
                                print 'Encountered exception in producer generator %s!' %producer_gen.__name__
                            err_q.put(conn.recv())
                    conn.close()
                    return 

                consumer_func(item, out_q)
        except Exception as e:
            with lock:
                if print_warns:
                    print 'Encountered exception in consumer function %s!' %consumer_func.__name__
                err_q.put(e)
            conn.close()

    conn_1, conn_2 = mp.Pipe()
    lock, err_q, out_q = mp.Lock(), mp.Queue(), mp.Queue()
    p1 = mp.Process(target=p_func, args=(conn_1,))
    p2 = mp.Process(target=c_func, args=(conn_2, lock, out_q, err_q))
    p1.start()
    p2.start()
    # we only need to wait for the consumer process to finish. It keeps going until it gets the 
    # 'None' sentinel from the producer *or* an exception.
    p2.join()
    if p1.is_alive():
        # might still be a live if there's an exception raised in the consumer.
        p1.terminate()
    if not err_q.empty():
        raise err_q.get()
    return out_q

def generate_and_consume_in_coroutine(producer_gen, consumer_coroutine, 
        print_warns=True, trust_coroutine_impl=False):
    """Same as generate_and_consume function, except the consumer is a coroutine.

    If you are not familiar with python coroutines, google them first. A coroutine is
    somewhat like a generator; it can maintain state, keep running indefinitely
    and is written in a style that resembles an ordinary function. They differ in their use
    of the yield keyword. A generator produces values using yield (which are retrieved by
    calling next()) whereas a coroutine receives input using yield (which is sent by calling send()).

    Given a generator function that produces objects for a handler coroutine to consume,
    set up a pipe between two subprocesses, then send the objects one at a time to
    the consumer coroutine.

    Why use a coroutine? So that you can maintain state inside the consumer and
    only produce output values into the queue when it makes sense (instead of having to do it
    from a stateless single function call as in the generate_and_consume function).

    Args:
        producer_gen (generator): Must yield any non-None object to be passed
            through a multiprocessing.Pipe to a handler function.
        consumer_coroutine (function): Must be a function that will return a coroutine 
            when called. The function must take one argument - a multiprocessing.Queue to which it 
            can optionally put output or results. The coroutine must handle all inputs 
            from the yield keyword, must also yield no outputs at all, and must exit 
            when a None object is sent to it. generate_and_consume_in_coroutine will send None as
            a sentinel to indicate that the coroutine should finish putting output in the Queue and return.
        print_warns (bool, optional): True by default. If an exception is caught
            in either the producer or consumer process, a line will be printed to
            stdout specifying this if set to True. Set False to suppress output.
        trust_coroutine_impl (bool, optional): False by default. Set this to True if you know
            that a call to inspect.getsourcelines(consumer_coroutine) will fail to find the source code
            for your coroutine (e.g. if you're running this in an interactive shell) and so will
            not be able to accurately validate it.

    Returns:
        multiprocessing.Queue: The results produced by the consumer coroutine.

    Raises:
        ValueError: If the producer generator yields a None or the consumer coroutine
            does not follow the above description (although whether it correctly handles
            the None sentinel indicating the need to exit is not validated.
        TypeError: If any of the arguments are invalid types.
        Exception: Any exceptions other than expected StopIteration raised by the two
            child processes will be caught and raised again in the parent process. 

    Example:
        An example of a generator::

            def gen():
                for i in range(10):
                    yield i
        
        A valid coroutine consumer::

            def co(out_q):
                tot = 0
                while True:
                    obj = yield
                    if obj is None:
                        out_q.put(tot)
                        return
                    tot += obj

        You would use these as follows::

            # set trust_coroutine_impl to be true if we're running from an interactive shell.
            out_q = generate_and_consume_in_coroutine(gen(), co, trust_coroutine_impl=True)
    
        The out_q would be a queue with one integer, being the sum of the numbers 0 to 9.

    """
    _validate_type('producer_gen', producer_gen, types.GeneratorType)
    _validate_type('consumer_coroutine', consumer_coroutine, types.FunctionType)
    _validate_type('print_warns', print_warns, types.BooleanType)
    if not trust_coroutine_impl and not _is_coroutine(consumer_coroutine):
        raise ValueError('Consumer coroutine %s code is invalid. ' %consumer_coroutine.__name__ +
            'yield keyword must only ever appear alone on a line (to drop sent input) ' + 
            'or to the rhs of an assignment operator.')        

    def p_func(conn):
        try:
            while True:
                obj = producer_gen.next()
                if obj is None:
                    raise ValueError('Producer generator %s produced a "None" value! Invalid.' 
                        %producer_gen.__name__)
                conn.send(obj)
        except Exception as e:
            # 'None' sentinel denotes completion
            conn.send(None)
            if not isinstance(e, StopIteration):
                # this indicates there was actually an error, so let's send it through.
                conn.send(e)
            conn.close()
    
    def c_func(conn, lock, out_q, err_q):
        # try to make our coroutine
        try:
            cons = consumer_coroutine(out_q)
            cons.next()
        except Exception as e:
            with lock:
                if print_warns:
                    print 'Encountered an exception trying to initialise ' + \
                        'consumer coroutine %s!' %consumer_coroutine.__name__
                err_q.put(e)
            conn.close()
            return
        
        try:
            stopiter_expected = False
            while True:
                item = conn.recv()
                if item is None:
                    # 'None' sentinel denotes completion, but check whether there was an exception...
                    if conn.poll(0.01):
                        # if there's something more in the queue, it means we've encountered an exception.
                        with lock:
                            if print_warns:
                                print 'Encountered exception in producer generator %s!' %producer_gen.__name__
                            err_q.put(conn.recv())
                    stopiter_expected = True
                    cons.send(None)
                    return
                cons.send(item)
        except Exception as e:
            if not isinstance(e, StopIteration) or not stopiter_expected:
                with lock:
                    if print_warns:
                        print 'Encountered exception in consumer coroutine %s!' %consumer_coroutine.__name__
                    err_q.put(e)
            conn.close()

    conn_1, conn_2 = mp.Pipe()
    lock, err_q, out_q = mp.Lock(), mp.Queue(), mp.Queue()
    p1 = mp.Process(target=p_func, args=(conn_1,))
    p2 = mp.Process(target=c_func, args=(conn_2, lock, out_q, err_q))
    p1.start()
    p2.start()
    # we only need to wait for the consumer process to finish. It keeps going until it gets the 
    # 'None' sentinel from the producer *or* an exception.
    p2.join()
    if p1.is_alive():
        # might still be a live if there's an exception raised in the consumer.
        p1.terminate()
    if not err_q.empty():
        raise err_q.get()
    return out_q
