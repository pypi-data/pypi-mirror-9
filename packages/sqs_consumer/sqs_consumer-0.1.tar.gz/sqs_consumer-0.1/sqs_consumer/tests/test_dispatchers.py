# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import unittest


class DispatcherTestCase(unittest.TestCase):
    pass


class JsonObjectDispatcherTestCase(unittest.TestCase):

    def test_found(self):
        from ..dispatchers import JsonObjectDispatcher
        from . import dispatcher_fake1

        target = JsonObjectDispatcher('key')
        target.scan(dispatcher_fake1)
        message = r'{"key":"value"}'
        self.assertDictEqual(target(message), {"key": "value"})

    def test_notfound(self):
        from ..dispatchers import JsonObjectDispatcher, CannotDispatch
        from . import dispatcher_fake1

        target = JsonObjectDispatcher('key')
        target.scan(dispatcher_fake1)
        message = r'{"key":"BLAH"}'
        self.assertRaises(CannotDispatch, target, message)
