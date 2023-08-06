# -*- coding: utf-8 -*-

import logging
import json
import venusian
from pyramid.path import caller_package
from zope.interface import implementer
from .interfaces import IApplication


logger = logging.getLogger(__name__)


class Registry(object):

    def __init__(self):
        self.registered = {}

    def add(self, value, ob):
        self.registered[value] = ob


class CannotDispatch(Exception):
    pass


class Dispatcher(object):

    def __init__(self):
        self.registry = Registry()
        self.scanner = venusian.Scanner(registry=self.registry)

    def __call__(self, data):
        raise NotImplementedError

    def scan(self, package=None):
        if package is None:
            package = caller_package()
        self.scanner.scan(package)


@implementer(IApplication)
class JsonObjectDispatcher(Dispatcher):

    key = None

    def __init__(self, key):
        super(JsonObjectDispatcher, self).__init__()
        self.key = key

    def __call__(self, data):
        try:
            decoded = json.loads(data)
        except ValueError:
            raise CannotDispatch(data)
        if isinstance(decoded, dict) and self.key in decoded:
            value = decoded[self.key]
            if value in self.registry.registered:
                logger.debug('Dispatch Message to %s', value)
                ob = self.registry.registered[value]
                return ob(decoded)
        raise CannotDispatch(data)


def task(value):
    def wrapper(wrapping):
        def callback(scanner, name, ob):
            scanner.registry.add(value, wrapping)
        venusian.attach(wrapping, callback)
        return wrapping
    return wrapper
