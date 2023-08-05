# -*- coding: utf-8 -*-

from kombu import Connection
from kombu.pools import producers
from unittest import TestResult
from time import time

UNITTEST_STATES = ['OK', None, 'FAIL', 'ERROR']


class CanopsisTestResult(TestResult):
    def __init__(self, connector_name, amqpuri, *args, **kwargs):
        super(CanopsisTestResult, self).__init__(*args, **kwargs)

        self.connector_name = connector_name
        self.amqpuri = amqpuri
        self.evts_to_send = []

    def testResult(self, test):
        for failure in self.failures:
            if failure[0] is test:
                return 2, failure[1]

        for error in self.errors:
            if error[0] is test:
                return 3, error[1]

        return 0, 'OK'

    def stopTest(self, test):
        module, testcase, testname = test.id().split('.')
        state, output = self.testResult(test)

        event = {
            'timestamp': int(time()),
            'connector': 'unittest',
            'connector_name': self.connector_name,
            'event_type': 'check',
            'source_type': 'resource',
            'component': testcase,
            'resource': testname,
            'state': state,
            'state_type': 1,
            'output': output
        }

        rk = '{}.{}.{}.{}.{}.{}'.format(
            event['connector'],
            event['connector_name'],
            event['event_type'],
            event['source_type'],
            event['component'],
            event['resource']
        )

        self.evts_to_send.append((rk, event))
        print('{0}... {1}'.format(rk, UNITTEST_STATES[state]))

    def gen_report(self):
        total = float(len(self.evts_to_send))
        nok = len([e for _, e in self.evts_to_send if e['state'] == 0])
        nfail = len([e for _, e in self.evts_to_send if e['state'] == 2])
        nerror = len([e for _, e in self.evts_to_send if e['state'] == 3])

        maxtests = max(nok, nfail, nerror)
        if maxtests == nerror:
            state = 3

        elif maxtests == nfail:
            state = 2

        else:
            state = 0

        event = {
            'timestamp': int(time()),
            'connector': 'unittest',
            'connector_name': self.connector_name,
            'event_type': 'check',
            'source_type': 'component',
            'component': 'report',
            'state': state,
            'perf_data_array': [
                {
                    'metric': 'nb_test_ok',
                    'value': nok,
                    'type': 'GAUGE'
                },
                {
                    'metric': 'nb_test_fail',
                    'value': nfail,
                    'type': 'GAUGE'
                },
                {
                    'metric': 'nb_test_error',
                    'value': nerror,
                    'type': 'GAUGE'
                },
                {
                    'metric': 'perc_test_ok',
                    'value': (nok / total) * 100.0,
                    'type': 'GAUGE',
                    'unit': '%'
                },
                {
                    'metric': 'perc_test_fail',
                    'value': (nfail / total) * 100.0,
                    'type': 'GAUGE',
                    'unit': '%'
                },
                {
                    'metric': 'perc_test_error',
                    'value': (nerror / total) * 100.0,
                    'type': 'GAUGE',
                    'unit': '%'
                }
            ],
            'output': '{} Test(s), {} OK(s), {} Fail(s), {} Error(s)'.format(
                total, nok, nfail, nerror
            )
        }

        rk = '{}.{}.{}.{}.{}'.format(
            event['connector'],
            event['connector_name'],
            event['event_type'],
            event['source_type'],
            event['component']
        )

        self.evts_to_send.append((rk, event))

        print('{0}... {1}'.format(rk, event['output']))

    def report(self):
        self.gen_report()

        with Connection(self.amqpuri) as conn:
            with producers[conn].acquire(block=True) as producer:
                for rk, event in self.evts_to_send:
                    producer.publish(
                        event,
                        serializer='json',
                        exchange='canopsis.events',
                        routing_key=rk
                    )
