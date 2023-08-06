# coding: utf-8

from barsup.controller import Controller


class Calc(Controller):

    def add(self, *, x, y=0):
        return x + y


class Hello(Controller):

    def greet(self, *, who):
        return "Hello, %s!" % who
