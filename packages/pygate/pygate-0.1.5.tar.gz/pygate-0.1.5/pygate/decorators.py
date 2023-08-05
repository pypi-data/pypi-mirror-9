
def accepts(*arg_schemas, **kwarg_schemas):
    def wrapper(func):
        def wrapped(*args,**kwargs):
            for arg,schema in zip(args,arg_schemas):
                if not schema(arg):
                    raise TypeError("Gate caught bad argument (%s)" %arg)
        
            for name,arg in kwargs.items():
                schema = kwarg_schemas[name]
                if not schema(arg):
                    raise TypeError("Gate caught bad argument (%s = %s)" %(name,arg))

            return func(*args,**kwargs)
        return wrapped;
    return wrapper;

def returns(return_schema):
    def wrapper(func):
        def wrapped(*args,**kwargs):
            ret = func(*args,**kwargs)
            if not return_schema(ret):
                raise TypeError("Gate caught bad return (%s)" %ret);
            return ret;
        return wrapped;
    return wrapper;
        
