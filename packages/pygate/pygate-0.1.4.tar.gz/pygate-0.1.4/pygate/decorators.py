class accepts():

    def __init__(self, *arg_schemas, **kwarg_schemas):
        self.arg_schemas = arg_schemas
        self.kwarg_schemas = kwarg_schemas
        
    def __call__(self, func):
        
        def wrapper(*args,**kwargs):
            for arg,schema in zip(args,self.arg_schemas):
                if not schema(arg):
                    raise TypeError("Gate caught bad argument (%s)" %arg);
        
            for name,arg in kwargs.items():
                schema = self.kwarg_schemas[name];
                if not schema(arg):
                    raise TypeError("Gate caught bad argument (%s = %s)" %(name,arg));

            return func(*args,**kwargs);
        
        return wrapper;
        

class returns():

    def __init__(self, return_schema):
        self.return_schema = return_schema

    def __call__(self, func):
        
        def wrapper(*args,**kwargs):
            ret = func(*args,**kwargs)
            if not self.return_schema(ret):
                raise TypeError("Gate caught bad return (%s)" %ret);
            return ret;
        
        return wrapper;
        
