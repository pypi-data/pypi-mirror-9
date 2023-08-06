# -*- coding: utf-8 -*-

import unittest


class WorkerTestCase(unittest.TestCase):

    def test_1(self):
        from ..workers import Worker
        target = Worker('callable', 'queue_name')
