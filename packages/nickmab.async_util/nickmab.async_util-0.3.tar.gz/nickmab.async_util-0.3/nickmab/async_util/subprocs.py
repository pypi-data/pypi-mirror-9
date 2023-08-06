__author__ = 'nickmab'

import types
from . import _utils
from _utils import validate_type as _validate_type
from _utils import is_coroutine as _is_coroutine
import multiprocessing as mp

'''Contains boilerplate code for working with common subprocess-related tasks.'''

def generate_and_consume(producer_gen, consumer_func, print_warns=True):
    '''Given a generator function that produces objects for a handler func,
    set up producer and consumer processes, then send the objects one at a time to
    the consumer function. The consumer must take two arguments: the object to process
    and a multiprocessing.Queue for putting output.'''
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

def generate_and_consume_in_coroutine(producer_gen, consumer_coroutine, print_warns=True):
    """Given a generator function that produces objects for a handler func,
    set up producer and consumer processes, then send the objects one at a time to
    the consumer coroutine (which must NOT yield anything; it should only accept input 
    objects via the "obj = (yield)" method - google python coroutines if unsure. 

    Why use a coroutine? So that you can maintain state inside the consumer function and
    only put output values into the queue when you want to (instead of having to do it
    on every single consumer function call). 

    Why not just use an nickmab.async_util.subprocs.generate_and_consume and simply
    point it to an instance function on a class to maintain state? I'm pretty sure that won't
    work properly across the process boundary (i.e. the member's state data won't be transferred
    properly - you'd have to solve this problem entirely differently using some kind of queue).

    The consumer must take one argument: a multiprocessing.Queue for putting output. 
    A 'None' sentinel value will be sent from this function to the coroutine to 
    indicate that the input has finished and it should put results in the output queue
    and return. This function guarantees that the producer generator can not produce
    a 'None' in the first place, so using None as a sentinel should never clash.

    An example of a generator:
    def gen():
        for i in range(10):
            yield i

    A valid coroutine consumer:
    def co(out_q):
    tot = 0
    while True:
        obj = yield
        if obj is None:
            out_q.put(tot)
            return
        tot += obj

    You would use these as follows:
    out_q = generate_and_consume_in_coroutine(gen(), co)
    
    The out_q would be a queue with one integer: the sum of the numbers 0 to 9."""
    _validate_type('producer_gen', producer_gen, types.GeneratorType)
    _validate_type('consumer_coroutine', consumer_coroutine, types.FunctionType)
    _validate_type('print_warns', print_warns, types.BooleanType)
    if not _is_coroutine(consumer_coroutine):
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
