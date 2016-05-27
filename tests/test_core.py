#!/usr/bin/env py.test
#
# Core class tests
#

from hostage.core import Handler, Result

class TestResultInvoke:
    def test_invokeFun(self):
        name = ["Reynolds"]

        def setter(val):
            name[0] = val

        Result("Mal")._invoke(setter)
        assert name[0] == "Mal"

    def test_invokeMethod(self):
        name = ["Washburne"]

        class Setter:
            def call(self, val):
                name[0] = val

        Result("Zoe")._invoke(Setter().call)
        assert name[0] == "Zoe"

    def test_invokeHandler(self):
        name = ["Washburne"]

        class MyHandler(Handler):
            def call(self, arg):
                name[0] = arg

        Result("Hoban")._invoke(MyHandler())


class MyHandler(Handler):
    def __init__(self, value=None):
        self.value = value

    def call(self, v):
        return v + "!"

class VarArgHandler(Handler):
    def call(self, *v):
        return ",".join(*v)

class TestHandlerInvoke:
    def test_invokeWithOwnValue(self):
        # If the handler was init'd with its own value,
        #  that value should override any incoming value
        handler = MyHandler("Independents")
        assert handler.invoke("Alliance") == "Independents!"

    def test_invokeWithoutValue(self):
        # If no "own" value, we use the provided
        assert MyHandler().invoke("Serenity") == "Serenity!"

    def test_invokeExpandTuple(self):
        assert VarArgHandler().invoke(("foo", "bar")) == "foo,bar"


class TestResultCalls:
    def test_orElse(self):
        # orElse executes the handler iff the value is falsy
        name = ["Reynolds"]
        def cb(arg):
            name[0] = arg

        Result(None).orElse(cb)
        assert name[0] is None

        Result("Mal").orElse(cb)
        assert name[0] is None

    def test_then(self):
        # then() executes the handler iff the value is truthy
        name = ["Reynolds"]
        def cb(arg):
            name[0] = arg

        Result(None).then(cb)
        assert name[0] == "Reynolds"

        Result("Mal").then(cb)
        assert name[0] == "Mal"

    def test_valueElse(self):
        # valueElse() returns the value iff the value is truthy,
        #  otherwise executes the handler
        name = ["Reynolds"]
        def cb(arg):
            name[0] = arg

        # no value? exec callback
        Result(None).valueElse(cb)
        assert name[0] == None

        # value? don't exec, but do return
        val = Result("Mal").valueElse(cb)
        assert val == "Mal"
        assert name[0] == None

    def test_chain(self):
        pass
