# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import logging
import signal
import botocore.session
from botocore_paste import session_from_config
from pyramid.settings import asbool


logger = logging.getLogger(__name__)
marker = object()


class Worker(object):

    client = None  # :type: botocore.client.sqs
    queue_url = None  # :type: str

    logger = logger
    stop = False

    def __init__(self, app, queue_name, session=None, receive_params=None,
                 protocol_dump=False):
        self.app = app
        self.queue_name = queue_name
        if session is None:
            session = botocore.session.get_session()
        self.session = session
        if receive_params is None:
            receive_params = {}
        self.receive_params = receive_params
        self.protocol_dump = protocol_dump
        self.stop = False

    def prepare(self):
        signal.signal(signal.SIGINT, self.handle_stop)
        signal.signal(signal.SIGQUIT, self.handle_stop)
        signal.signal(signal.SIGTERM, self.handle_stop)
        self.client = self.session.create_client('sqs')
        self.queue_url = self.get_queue_url()

    def handle_stop(self, sig, frame):
        self.logger.info('Received signal %r', sig)
        self.stop = True

    def serve_forever(self):
        self.prepare()
        self.logger.info('Start polling to %s', self.queue_name)
        while not self.stop:
            self.serve_oneshot()
        self.logger.info('Finish polling to %s', self.queue_name)

    def serve_oneshot(self):
        recv_ret = self.receive_messages()
        if 'Messages' in recv_ret:
            self.logger.debug('Polled: %d messages', len(recv_ret['Messages']))
            for message in recv_ret['Messages']:
                self.run_app(message)
        else:
            # self.logger.debug('Polled: no messages')
            pass

    def get_queue_url(self):
        params = dict(QueueName=self.queue_name)
        if self.protocol_dump:
            self.logger.debug('[PROTO] GetQueueUrl Call: %r', params)
        ret = self.client.get_queue_url(**params)
        if self.protocol_dump:
            self.logger.debug('[PROTO] GetQueueUrl Return: %r', ret)
        return ret['QueueUrl']

    def receive_messages(self):
        params = dict(QueueUrl=self.queue_url)
        params.update(self.receive_params)
        if self.protocol_dump:
            self.logger.debug('[PROTO] ReceiveMessage Call: %r', params)
        ret = self.client.receive_message(**params)
        if self.protocol_dump:
            self.logger.debug('[PROTO] ReceiveMessage Return: %r', ret)
        return ret

    def delete_message(self, message):
        params = dict(QueueUrl=self.queue_url,
                      ReceiptHandle=message['ReceiptHandle'])
        if self.protocol_dump:
            self.logger.debug('[PROTO] DeleteMessage Call: %r', params)
        ret = self.client.delete_message(**params)
        if self.protocol_dump:
            self.logger.debug('[PROTO] DeleteMessage Return: %r', ret)
        return ret

    def run_app(self, message):
        message_id = message['MessageId']
        self.logger.info('Process Message: %s', message_id)
        body = message['Body']
        self.logger.debug('Message Body: %r', body)
        ret = None
        try:
            ret = self.app(body)
        except:
            self.logger.exception('Consumer Halted')
        if ret:
            self.logger.info('Delete Message: %s', message_id)
            self.delete_message(message)


def run_pserve(app, global_config, **settings):
    """
    :param app: callable
    :param global_config: dict
    :param settings: dict
    :return: int
    """
    params = {
        'app': app,
        'queue_name': settings['queue_name'],
        'protocol_dump': asbool(settings.get('protocol_dump')),
        'session': session_from_config(settings, 'botocore.')
    }
    receive_params = {}
    for k, kk in (('max_number_of_messages', 'MaxNumberOfMessages'),
                  ('visibility_timeout', 'VisibilityTimeout'),
                  ('wait_time_seconds', 'WaitTimeSeconds')):
        k = 'sqs.' + k
        if k in settings and len(settings[k]) > 0:
            params[kk] = int(settings[k])
    params['receive_params'] = receive_params
    worker = Worker(**params)
    worker.serve_forever()
    return 0
