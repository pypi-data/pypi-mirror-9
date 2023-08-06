from __future__ import print_function

import os
import sys
import time
from collections import defaultdict

import pytest
from process_tests import dump_on_error
from process_tests import TestProcess
from process_tests import wait_for_strings
from redis import StrictRedis

from redis_lock import Lock, AlreadyAcquired, NotAcquired
from redis_lock import reset_all

from conf import TIMEOUT
from conf import UDS_PATH
from conf import HELPER


@pytest.yield_fixture
def redis_server(scope='module'):
    try:
        os.unlink(UDS_PATH)
    except OSError:
        pass
    with TestProcess('redis-server', '--port', '0', '--unixsocket', UDS_PATH) as process:
        wait_for_strings(process.read, TIMEOUT, "Running")
        yield process


@pytest.fixture(scope='function')
def conn(redis_server):
    return StrictRedis(unix_socket_path=UDS_PATH)


def test_simple(redis_server):
    with TestProcess(sys.executable, HELPER, 'test_simple') as proc:
        with dump_on_error(proc.read):
            name = 'lock:foobar'
            wait_for_strings(
                proc.read, TIMEOUT,
                'Getting %r ...' % name,
                'Got lock for %r.' % name,
                'Releasing %r.' % name,
                'UNLOCK_SCRIPT not cached.',
                'DIED.',
            )


def test_no_block(conn):
    with Lock(conn, "foobar"):
        with TestProcess(sys.executable, HELPER, 'test_no_block') as proc:
            with dump_on_error(proc.read):
                name = 'lock:foobar'
                wait_for_strings(
                    proc.read, TIMEOUT,
                    'Getting %r ...' % name,
                    'Failed to get %r.' % name,
                    'acquire=>False',
                    'DIED.',
                )


def test_expire(conn):
    with Lock(conn, "foobar", expire=TIMEOUT/4):
        with TestProcess(sys.executable, HELPER, 'test_expire') as proc:
            with dump_on_error(proc.read):
                name = 'lock:foobar'
                wait_for_strings(
                    proc.read, TIMEOUT,
                    'Getting %r ...' % name,
                    'Got lock for %r.' % name,
                    'Releasing %r.' % name,
                    'UNLOCK_SCRIPT not cached.',
                    'DIED.',
                )
    lock = Lock(conn, "foobar")
    try:
        assert lock.acquire(blocking=False) == True
    finally:
        lock.release()


def test_double_acquire(conn):
    lock = Lock(conn, "foobar")
    with lock:
        pytest.raises(RuntimeError, lock.acquire)
        pytest.raises(AlreadyAcquired, lock.acquire)


def test_plain(conn):
    with Lock(conn, "foobar"):
        time.sleep(0.01)


def test_no_overlap(redis_server):
    with TestProcess(sys.executable, HELPER, 'test_no_overlap') as proc:
        with dump_on_error(proc.read):
            name = 'lock:foobar'
            wait_for_strings(proc.read, TIMEOUT, 'Getting %r ...' % name)
            wait_for_strings(proc.read, TIMEOUT, 'Got lock for %r.' % name)
            wait_for_strings(proc.read, TIMEOUT, 'Releasing %r.' % name)
            wait_for_strings(proc.read, TIMEOUT, 'UNLOCK_SCRIPT not cached.')
            wait_for_strings(proc.read, 10*TIMEOUT, 'DIED.')

            class Event(object):
                pid = start = end = '?'

                def __str__(self):
                    return "Event(%s; %r => %r)" % (self.pid, self.start, self.end)

            events = defaultdict(Event)
            for line in proc.read().splitlines():
                try:
                    pid, time, junk = line.split(' ', 2)
                    pid = int(pid)
                except ValueError:
                    continue
                if 'Got lock for' in junk:
                    events[pid].pid = pid
                    events[pid].start = time
                if 'Releasing' in junk:
                    events[pid].pid = pid
                    events[pid].end = time
            assert len(events) == 125

            for event in events.values():
                for other in events.values():
                    if other is not event:
                        try:
                            if other.start < event.start < other.end or \
                               other.start < event.end < other.end:
                                pytest.fail('%s overlaps %s' % (event, other))
                        except:
                            print("[%s/%s]" % (event, other))
                            raise

def test_reset(conn):
    with Lock(conn, "foobar") as lock:
        lock.reset()
        new_lock = Lock(conn, "foobar")
        new_lock.acquire(blocking=False)
        new_lock.release()


def test_reset_all(conn):
    lock1 = Lock(conn, "foobar1")
    lock2 = Lock(conn, "foobar2")
    lock1.acquire(blocking=False)
    lock2.acquire(blocking=False)
    reset_all(conn)
    lock1 = Lock(conn, "foobar1")
    lock2 = Lock(conn, "foobar2")
    lock1.acquire(blocking=False)
    lock2.acquire(blocking=False)
    lock1.release()
    lock2.release()


def test_owner_id(conn):
    unique_identifier = b"foobar-identifier"
    lock = Lock(conn, "foobar-tok", expire=TIMEOUT/4, id=unique_identifier)
    lock_id = lock.id
    assert lock_id == unique_identifier
    lock.acquire(blocking=False)
    assert lock.get_owner_id() == unique_identifier
    lock.release()


def test_token(conn):
    lock = Lock(conn, "foobar-tok")
    tok = lock.id
    assert conn.get(lock._name) is None
    lock.acquire(blocking=False)
    assert conn.get(lock._name) == tok


def test_bogus_release(conn):
    lock = Lock(conn, "foobar-tok")
    pytest.raises(NotAcquired, lock.release)
    lock.release(force=True)

def test_release_from_nonblocking_leaving_garbage(conn):
    for _ in range(10):
        lock = Lock(conn, 'release_from_nonblocking')
        lock.acquire(blocking=False)
        lock.release()
        assert conn.llen('lock-signal:release_from_nonblocking') == 1
