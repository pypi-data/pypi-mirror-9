from random import choice as randchoice

def cache(func, **kwargs):
    """ Simple function caching decorator. """
    call = None
    try:
        from functools import lru_cache # Python 3 LRU cache = good
    except ImportError as e:
        # No Python 3
        maxsize = kwargs.get('maxsize', 32)
        cdict = {}
        def call(*args, **kwargs):
            keystruct = tuple(args), tuple(kwargs.items())
            key = hash(keystruct)
            if key in cdict:
                return cdict[key]
            newresult = func(*args, **kwargs)
            if len(cdict)>maxsize:
                del cdict[randchoice(cdict.keys())]
            cdict[key] = newresult
            return newresult
    else:
        call = lru_cache(**kwargs)(func)
    finally:
        return call
    
