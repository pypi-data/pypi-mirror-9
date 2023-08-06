import os

SERIAL = 'yaul.parallel.SERIAL'
THREADED = 'yaul.parallel.THREADED'
MULTIPROCESSED = 'yaul.parallel.MULTIPROCESSED'
PARALLEL_TYPES = [SERIAL, THREADED, MULTIPROCESSED]
_DEFAULT = SERIAL

def set_default_parallel(parallel_type):
    if not parallel_type in PARALLEL_TYPES:
        raise ValueError("Unrecognized parallelism type", parallel_type)
    global _DEFAULT
    _DEFAULT = parallel_type

class GenericPool(object):
    """Generic pool class supporting multiple kinds of parallelism."""
    
    def __init__(self, parallel_type=None, num_threads=None):
        if not parallel_type:
            parallel_type = _DEFAULT
        if not parallel_type in PARALLEL_TYPES:
            raise ValueError("Unrecognized parallelism type", parallel_type)
        self.partype = parallel_type
        self.num_threads = None
        self.pool = None

    def get_mapper(self):
        if self.partype == SERIAL:
            return self.__map_serial
        if self.partype == THREADED:
            return self.__map_threaded
        if self.partype == MULTIPROCESSED:
            return self.__map_multiprocessed
        raise ValueError("Unrecognized parallelism type", parallel_type)

    def map_reduce(self, mapfunc, collection, reducer=None, blocking=False):
        if not reducer:
            reducer = self.__null_reducer
        mapper = self.get_mapper()
        results = mapper(mapfunc, collection)
        reduced_results = reducer(results)
        if blocking:
            final_results = [x for x in reduced_results]
            return final_results
        else:
            return iter(reduced_results)

    def dump_pool(self):
        if self.pool:
            self.pool.close()
            self.pool = None

    def __null_reducer(self, vals):
        return vals

    def __map_serial(self, mapfunc, collection):
        for v in collection:
            yield mapfunc(v)
    
    def __map_pool(self, mapfunc, collection, pool):
        return pool.imap(mapfunc, collection)
    
    def __map_multiprocessed(self, mapfunc, collection):
        from multiprocessing import Pool, cpu_count
        procs = self.num_threads or (min(cpu_count(), 16) if cpu_count() else 1)
        if not self.pool:
            self.pool = Pool(procs)
        return self.__map_pool(mapfunc, collection, self.pool)
    
    def __map_threaded(self, mapfunc, collection):
        from multiprocessing.pool import ThreadPool
        from multiprocessing import cpu_count
        procs = self.num_threads or (min(cpu_count(), 16) if cpu_count() else 1)
        if not self.pool:
            self.pool = ThreadPool(procs)
        return self.__map_pool(mapfunc, collection, self.pool)
