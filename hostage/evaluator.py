
from abc import ABCMeta, abstractmethod
import inspect

class _Proxy:
    def __init__(self, obj, handler, Result):
        self._obj = obj
        self._handler = handler
        self.Result = Result

    def __getattr__(self, attrib):
        """Wraps execution of methods in _handler
        """
        attr = getattr(self._obj, attrib)
        if inspect.ismethod(attr):
            def _delegate(*args, **kwargs):
                return self._handler(self.Result, self._obj, attr, *args, **kwargs)
            return _delegate

        return attr

def _justVerify(Result, delegate, method, *args, **kwargs):
    return Result(method(*args, **kwargs))

def _dryHandle(Result, delegate, method, *args, **kwargs):
    cls = delegate.__class__.__name__
    met = method.__name__

    params = ",".join([repr(p) for p in delegate.params])
    args = ",".join([repr(a) for a in args])
    kwargs = ",".join(["%s=%s" % (k, repr(v)) for k, v in kwargs.iteritems()])
    if kwargs and args:
        kwargs = "," + kwargs

    print("* DRYRUN: %s(%s).%s(%s%s)" % (cls, params, met, args, kwargs))
    return Result(True)

class Evaluator:
    __metaclass__ = ABCMeta

    def __init__(self, *params):
        self.params = params

    def _toVerifier(self, Result):
        return _Proxy(self, _justVerify, Result)

    def _toDryVerifier(self, Result):
        return _Proxy(self, _dryHandle, Result)
