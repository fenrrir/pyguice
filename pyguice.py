#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from functools import wraps

_current_injection_configuration = None


def get_dependencies(function):
    params = {}
    annotations = function.__annotations__
    configuration = get_configuration()

    for name, ptype in annotations.items():

        interface_impl = getattr(ptype, "binding", None)

        if interface_impl:
            params[name] = configuration.get(ptype)()
        else:
            params[name] = ptype()

    return params




def inject(function): # functions

    @wraps(function)
    def newfunction():
        params = get_dependencies(function)
        return function(**params)
    
    return newfunction


def Inject(method): # methods

    @wraps(method)
    def newmethod(self):
        params = get_dependencies(method)
        return method(self, **params)
    
    return newmethod


def ImplementedBy(cls):

    def inner(interface):
        interface.binding = Binding()
        interface.binding.add('default', cls)
        return interface

    return inner


class Binding:

    def __init__(self):
        self.conf = {}

    def add(self, name, impl):
        self.conf[name] =  impl

    def get(self, name):
        return self.conf[name]



class Configuration:


    def __init__(self, name='default'):
        self.name = name

    def bind(self, interface, impl):

        if not hasattr(interface, "binding"):
            interface.binding = Binding()
        interface.binding.add(self.name, impl)

        return self

    def get(self, interface):
        return interface.binding.get(self.name)

    def deploy(self):
        set_configuration(self)




def set_configuration(configuration):
    global _current_injection_configuration
    _current_injection_configuration = configuration


def get_configuration():
    if not _current_injection_configuration:
        return Configuration()
    return _current_injection_configuration


def test():

    class ImplHello:

        def say_hello(self):
            return "Hello World"


    class MockHello:


        def say_hello(self):
            pass


    @ImplementedBy(ImplHello)
    class Hello:

        def say_hello(self):
            raise



    class Test:

        @Inject
        def __init__(self, hello : Hello):
            self.hello = hello


        def run(self):
            return self.hello.say_hello()




    t = Test()
    assert t.run() == "Hello World"

    Configuration('test').bind(Hello, MockHello).deploy()

    t = Test()
    assert t.run() == None





if __name__ == "__main__":
    test()
