class MethodMissing(object):
    def __getattr__(self, name):
        try:
            return self.__getattribute__(name)
        except AttributeError:
            def method(*args, **kw):
                return self.method_missing(name, *args, **kw)
            return method

    def method_missing(self, name, *args, **kw):
        raise AttributeError("%r object has no attribute %r" %
                             (self.__class__, name))

class ValMissing(object):
    def __getattr__(self, name):
        try:
            return self.__getattribute__(name)
        except AttributeError:
            return self.val_missing(name)

    def val_missing(self, name):
        raise AttributeError("%r object has no attribute %r" %
                             (self.__class__, name))

