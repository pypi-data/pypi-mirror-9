#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import find_packages, setup


description = 'AWS SQS Consumer helper'
here = os.path.abspath(os.path.dirname(__file__))
try:
    readme = open(os.path.join(here, 'README.rst')).read()
    changes = open(os.path.join(here, 'CHANGES.txt')).read()
    long_description = '\n\n'.join([readme, changes])
except:
    long_description = description


requires = (
    'botocore',
    'botocore_paste',
    'pyramid',
    'venusian',
)

setup(
    name='sqs_consumer',
    version='0.1',
    description=description,
    long_description=long_description,
    author='OCHIAI, Gouji',
    author_email='gjo.ext@gmail.com',
    url='https://github.com/gjo/sqs_consumer',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    test_suite='sqs_consumer',
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
    ],
    entry_points="""\
    [paste.app_factory]
    example = sqs_consumer.tests.example:main
    [paste.server_runner]
    runworker = sqs_consumer.workers:run_pserve
    """,
)
