# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from ..dispatchers import task


@task('value')
def test(data):
    return data
