# -*- coding:utf-8; tab-width:4; mode:python -*-

from unittest import TestCase
import hamcrest

from commodity.testing import wait_that, call_with
from doublex import Stub


class A(object):
    def __init__(self):
        self.n = 0

    def foo(self, arg):
        if self.n < 2:
            self.n += 1
            return 10

        return arg * 100

    def raise_exc(self, value):
        raise Exception


class call_with_tests(TestCase):
    def setUp(self):
        self.stub = Stub()
        with self.stub:
            self.stub.foo().delegates([1, 10, 20, 100])
            self.stub.raise_exc().raises(Exception)

    def test_wait_with_expected_value(self):
        wait_that(self.stub.foo, call_with().returns(100), delta=0.1, timeout=1)

    def test_FAIL_wait_with_expected_value(self):
        try:
            wait_that(self.stub.foo, call_with().returns(200), delta=0.1, timeout=1)
            self.fail()
        except AssertionError:
            pass

    def test_wait_no_exception(self):
        wait_that(self.stub.foo, call_with(), delta=0.1)

    def test_FAIL_wait_no_exception(self):
        try:
            wait_that(self.stub.raise_exc, call_with(), delta=0.1, timeout=1)
            self.fail()
        except AssertionError:
            pass

    def test_matcher(self):
        wait_that(self.stub.foo, call_with().returns(hamcrest.is_not(None)))
