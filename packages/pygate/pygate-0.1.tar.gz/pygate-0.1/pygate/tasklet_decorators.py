from google.appengine.ext import ndb

class yields():

    def __init__(self, yield_schema):
        self.return_schema = return_schema

    def __call__(self, func):
        
        @ndb.tasklet
        def wrapper(*args,**kwargs):
            ret = yield func(*args,**kwargs)
            if self.return_schema(ret):
                raise ndb.Return(ret)
            else:
                raise TypeError("Gate caught bad yield (%s)" %ret);

