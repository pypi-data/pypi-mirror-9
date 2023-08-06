__author__ = 'nickmab'

'''Module for doing web requests with the help of nickmab.async_util.threads module.'''

import types
import urllib2
import json
from . import threads as thr
from _utils import validate_type as _validate_type

class JSONQueryPool:
    '''Class for grouping together many web requests which should return JSON data,
    running them asynchronously, storing the results and automatically parsing to py objs.'''
    def __init__(self, num_worker_threads=5, queries={}):
        '''Takes a dict of { 'query_str_label': 'query_url' } which should consist of
        queries that return a JSON object which will later be retrieved and parsed.'''
        # first define a function that we're going to use to fetch url results.
        def fetch_json_object(url):
            '''Naively try to fetch a JSON result from the given url and return
            a parsed python object. Let the FuncWrap handle any exceptions.'''
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
        # skipping validation for now, will add this code later

    @property
    def is_finished(self):
        return bool(self.result)

    @property
    def has_exception(self):
        if not self.result:
            return False
        return any(isinstance(r, Exception) for r in self.result.values())

    def run(self):
        '''Run the queries in the FuncWrapPool, await results and then collect them in
        self.result in the form { 'query_str_label': result_obj } where the result_obj
        is either a parsed python result if it worked or an exception if it didn't!'''
        self.pool.run()
        for fw in self.func_wraps:
            if fw.exception:
                self.result[fw.name] = fw.exception
            else:
                self.result[fw.name] = fw.result
            
