def isNone(arg):
    return arg == None

def isNotNone(arg):
    return arg != None
    
def exists(arg):
    return arg != None

def isTrue(arg):
    return arg == True
    
def isFalse(arg):
    return arg == False
    
def isBool(arg):
    return isinstance(arg, bool)       
    
def isInt(arg):
    return isinstance(arg, (int, long))

def isString(arg):
    return isinstance(arg, basestring)

def isList(arg):
    return isinstance(arg, list)
    
def isTuple(arg):
    return isinstance(arg, tuple)

def isDict(arg):
    return isinstance(arg, dict)

def isCallable(arg):
    return callable(arg)
    
def isInstance(instance):
    def func(arg):
        return isinstance(arg, instance)
    return func

def isOneOf(*schemas):
    def func(arg):
        for s in schemas:
            if s(arg):
                return True
        return False
    return func

def isAllOf(*schemas):
    def func(arg):
        for s in schemas:
            if not s(arg):
                return False
        return True
    return func

