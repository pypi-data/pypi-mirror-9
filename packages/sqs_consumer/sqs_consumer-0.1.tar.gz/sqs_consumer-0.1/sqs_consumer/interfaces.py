# -*- coding: utf-8 -*-

from zope.interface import Interface


class IApplication(Interface):
    def __call__(data):
        """
        Return true if processes for `data` is done and worker can
        remove message from broker.

        :type data: str
        :rtype: bool
        """
