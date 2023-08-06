#!/usr/bin/env python

from __future__ import absolute_import, print_function

import datetime
import threading
import time

import mock
import pykka

from . import pykka_timeout

no_sleep = mock.patch('time.sleep', lambda n: None)

def arvados_node_mock(node_num=99, job_uuid=None, age=-1, **kwargs):
    mod_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=age)
    mod_time_s = mod_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    if job_uuid is True:
        job_uuid = 'zzzzz-jjjjj-jobjobjobjobjob'
    crunch_worker_state = 'idle' if (job_uuid is None) else 'busy'
    node = {'uuid': 'zzzzz-yyyyy-{:015x}'.format(node_num),
            'created_at': '2014-01-01T01:02:03.04050607Z',
            'modified_at': mod_time_s,
            'first_ping_at': kwargs.pop('first_ping_at', mod_time_s),
            'last_ping_at': mod_time_s,
            'slot_number': node_num,
            'hostname': 'compute{}'.format(node_num),
            'domain': 'zzzzz.arvadosapi.com',
            'ip_address': ip_address_mock(node_num),
            'job_uuid': job_uuid,
            'crunch_worker_state': crunch_worker_state,
            'info': {'ping_secret': 'defaulttestsecret'}}
    node.update(kwargs)
    return node

def cloud_object_mock(name_id, **extra):
    # A very generic mock, useful for stubbing libcloud objects we
    # only search for and pass around, like locations, subnets, etc.
    cloud_object = mock.NonCallableMagicMock(['id', 'name'],
                                             name='cloud_object')
    cloud_object.name = str(name_id)
    cloud_object.id = 'id_' + cloud_object.name
    cloud_object.extra = extra
    return cloud_object

def cloud_node_mock(node_num=99, **extra):
    node = mock.NonCallableMagicMock(
        ['id', 'name', 'state', 'public_ips', 'private_ips', 'driver', 'size',
         'image', 'extra'],
        name='cloud_node')
    node.id = str(node_num)
    node.name = node.id
    node.public_ips = []
    node.private_ips = [ip_address_mock(node_num)]
    node.extra = extra
    return node

def cloud_node_fqdn(node):
    # We intentionally put the FQDN somewhere goofy to make sure tested code is
    # using this function for lookups.
    return node.extra.get('testname', 'NoTestName')

def ip_address_mock(last_octet):
    return '10.20.30.{}'.format(last_octet)

class MockShutdownTimer(object):
    def _set_state(self, is_open, next_opening):
        self.window_open = lambda: is_open
        self.next_opening = lambda: next_opening


class MockSize(object):
    def __init__(self, factor):
        self.id = 'z{}.test'.format(factor)
        self.name = self.id
        self.ram = 128 * factor
        self.disk = 100 * factor
        self.bandwidth = 16 * factor
        self.price = float(factor)
        self.extra = {}

    def __eq__(self, other):
        return self.id == other.id


class MockTimer(object):
    def __init__(self, deliver_immediately=True):
        self.deliver_immediately = deliver_immediately
        self.messages = []
        self.lock = threading.Lock()

    def deliver(self):
        with self.lock:
            to_deliver = self.messages
            self.messages = []
        for callback, args, kwargs in to_deliver:
            callback(*args, **kwargs)

    def schedule(self, want_time, callback, *args, **kwargs):
        with self.lock:
            self.messages.append((callback, args, kwargs))
        if self.deliver_immediately:
            self.deliver()


class ActorTestMixin(object):
    FUTURE_CLASS = pykka.ThreadingFuture
    TIMEOUT = pykka_timeout

    def tearDown(self):
        pykka.ActorRegistry.stop_all()

    def stop_proxy(self, proxy):
        return proxy.actor_ref.stop(timeout=self.TIMEOUT)

    def wait_for_assignment(self, proxy, attr_name, unassigned=None,
                            timeout=TIMEOUT):
        deadline = time.time() + timeout
        while True:
            loop_timeout = deadline - time.time()
            if loop_timeout <= 0:
                self.fail("actor did not assign {} in time".format(attr_name))
            result = getattr(proxy, attr_name).get(loop_timeout)
            if result is not unassigned:
                return result


class DriverTestMixin(object):
    def setUp(self):
        self.driver_mock = mock.MagicMock(name='driver_mock')
        super(DriverTestMixin, self).setUp()

    def new_driver(self, auth_kwargs={}, list_kwargs={}, create_kwargs={}):
        create_kwargs.setdefault('ping_host', '100::')
        return self.TEST_CLASS(
            auth_kwargs, list_kwargs, create_kwargs,
            driver_class=self.driver_mock)

    def driver_method_args(self, method_name):
        return getattr(self.driver_mock(), method_name).call_args


class RemotePollLoopActorTestMixin(ActorTestMixin):
    def build_monitor(self, *args, **kwargs):
        self.timer = mock.MagicMock(name='timer_mock')
        self.client = mock.MagicMock(name='client_mock')
        self.subscriber = mock.Mock(name='subscriber_mock')
        self.monitor = self.TEST_CLASS.start(
            self.client, self.timer, *args, **kwargs).proxy()
