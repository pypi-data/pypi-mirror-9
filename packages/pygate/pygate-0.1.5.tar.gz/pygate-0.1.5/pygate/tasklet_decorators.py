from google.appengine.ext import ndb

def yields(yield_schema):
    def wrapper(func):
        def wrapped(*args,**kwargs):
            ret = yield func(*args,**kwargs)
            if yield_schema(ret):
                raise ndb.Return(ret)
            else:
                raise TypeError("Gate caught bad yield (%s)" %ret);
        return wrapped;
    return wrapper;
