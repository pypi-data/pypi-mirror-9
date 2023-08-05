

class Options(dict):
    def __init__(self, dictionary, obj):
        self.obj = obj
        self.update(dictionary)

    def __getitem__(self, name):
        if self.has_key(name):
            return dict.get(self, name)
        if hasattr(self.obj, name):
            return getattr(self.obj, name)
        raise KeyError("Can't find option: %s" % name)

    def __getattr__(self, name):
        return self[name]

class A(object):
    optional1 = '1'
    arg2 = '4'
    start = False
    pot = None
    def __init__(self, **kwargs):
        self.o = Options(kwargs, self)

a = A(arg2='Martin', start=True)
print a.o.arg2
print a.o
print a.o.start
print a.o['optional1']
print a.o.pot
print a.o.error

