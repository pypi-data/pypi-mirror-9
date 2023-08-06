__author__ = 'nickmab'

import types
from . import _utils
from _utils import validate_type as _validate_type
import multiprocessing as mp

'''Contains convenience classes for working with basic ThreadPools and similar basic tasks.'''

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
                    break

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

