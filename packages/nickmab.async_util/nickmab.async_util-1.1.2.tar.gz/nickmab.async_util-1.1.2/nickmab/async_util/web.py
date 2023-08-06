__author__ = 'nickmab'

"""Module for doing web requests with the help of nickmab.async_util.threads module."""

import types
import urllib2
import json
from . import threads as thr
from _utils import validate_type as _validate_type

class JSONQueryPool(object):
    """Run JSON web requests in a ThreadPool, collect and parse results into a python obj.

    This class actually uses a nickmab.async_util.threads.FuncWrapPool to hand out jobs
    to worker threads and then collect the results. The results will be collected in a dict
    of python objects, being either the parsed JSON result or an exception raised in a
    worker thread.

    Whilst the jobs are run asynchronously, a call to JSONQueryPool.run is blocking.

    Attributes:
        result (dict): The results dict, which will be empty before the workers have returned
            and of the form { 'query_str_label': result_obj } where the label is provided
            per query in the class __init__  

    Examples:
        Let's imagine we have two urls http://foo.bar/bas and http://bas.bar/foo that return
        (as JSON string) a list [1, 2, 3] and a dict { 'a': 'b } respectively. 

        We can fetch these as follows::

            # create a pool with the details - note the query { 'name': 'url' } format 
            qp = JSONQueryPool(num_worker_threads=2, queries={
                'bas_list': 'http://foo.bar.bas', 'foo_dict': 'http://bas.bar/foo' }) 
            
            # run both queries at once and collect the results (this call blocks til done)
            qp.run()

        Now we have our results in the result dict and can fetch them::

            if not qp.has_exception:
                l = qp.result['bas_list']
                d = qp.result['foo_dict']
            else:
                # do some other exception handling...
                for k, v in qp.result.iteritems():
                    if isinstance(v, Exception):
                        print 'Encountered exception in %s query: %s' %(k, v)

    """
    def __init__(self, num_worker_threads=5, queries={}):
        """init by specifying number of worker threads, query names / identifiers and urls.

        Does not run immediately. Some basic validation is performed and we wait for a call to run().

        Args:
            num_worker_threads (int, optional): Number of worker threads in the ThreadPool, default 5.
            queries (dict): { str: str } dict of 'query_name': 'query_url' where the name is later
                used to identify each individual query in the result dict.

        Raises:
            ValueError: If no query dictionary is provided.
            TypeError: If any of the arguments provided are the wrong type.

        """
        # first define a function that we're going to use to fetch url results.
        def fetch_json_object(url):
            # Naively try to fetch a JSON result from the given url and return
            # a parsed python object. Let the FuncWrap handle any exceptions.
            res = urllib2.urlopen(url)
            return json.loads(res.read())
        
        # validation and initialisation is done inline here.
        if not queries:
            raise ValueError('Must provide at least one pending query! Got none!')
        _validate_type('num_worker_threads', num_worker_threads, types.IntType) 
        _validate_type('queries', queries, types.DictType)
        
        self.func_wraps = []
        for q_name, q_url in queries.iteritems():
            try:
                _validate_type('', q_name, types.StringType)
                _validate_type('', q_url, types.StringType)
            except TypeError:
                raise TypeError('queries must be a dict of "str_query_name/id": "str_url_to_fetch". ' + 
                    'Instead, got %s: %s in %s' %(q_name, q_url, queries))

            self.func_wraps.append(
                thr.FuncWrap(target=fetch_json_object, name=q_name, args=(q_url,))
            )
        
        self.pool = thr.FuncWrapPool(num_worker_threads, self.func_wraps)
        self.result = {}

    @property
    def is_finished(self):
        """True iff all jobs have finished, regardless of whether there was an exception.

        Returns: 
            bool: Indicates whether all requests have returned either an exception or some result.

        """
        return bool(self.result)

    @property
    def has_exception(self):
        """True iff all jobs have finished and any one of them encountered an exception.

        Returns:
            bool: Indicates whether an exception was raised whilst running any of the requests.

        """
        if not self.result:
            return False
        return any(isinstance(r, Exception) for r in self.result.values())

    def run(self):
        """Run all queries in the pool, await results and collect them in self.result dict.

        When each worker returns (or exits following an exception), the return value (or exception)
        is collected in the self.result dict, which is of the form { 'query_str_label': result_obj }

        Note that the results will automatically be parsed from JSON into python objects.

        Returns:
            None: The return value (or exception) of all queries is stored in the self.result dict.

        """
        self.pool.run()
        for fw in self.func_wraps:
            if fw.exception:
                self.result[fw.name] = fw.exception
            else:
                self.result[fw.name] = fw.result
            
