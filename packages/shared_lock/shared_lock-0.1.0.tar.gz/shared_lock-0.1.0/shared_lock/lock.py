# -*- coding: utf-8 -*-

# Copyright (C) 2014 Yahoo! Inc. All Rights Reserved.
# Copyright 2011 OpenStack Foundation.
#
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import collections
import contextlib
import threading

from oslo_utils import importutils
import six

# Used for the reader-writer lock get the right thread 'hack' (needed below).
eventlet = importutils.try_import('eventlet')
eventlet_patcher = importutils.try_import('eventlet.patcher')


def read_locked(*args, **kwargs):
    """Acquires & releases a read lock around call into decorated method.

    NOTE(harlowja): if no attribute name is provided then by default the
    attribute named '_lock' is looked for (this attribute is expected to be
    the rw-lock object) in the instance object this decorator is attached to.
    """

    def decorator(f):
        attr_name = kwargs.get('lock', '_lock')

        @six.wraps(f)
        def wrapper(self, *args, **kwargs):
            rw_lock = getattr(self, attr_name)
            with rw_lock.read_lock():
                return f(self, *args, **kwargs)

        return wrapper

    # This is needed to handle when the decorator has args or the decorator
    # doesn't have args, python is rather weird here...
    if kwargs or not args:
        return decorator
    else:
        if len(args) == 1:
            return decorator(args[0])
        else:
            return decorator


def write_locked(*args, **kwargs):
    """Acquires & releases a write lock around call into decorated method.

    NOTE(harlowja): if no attribute name is provided then by default the
    attribute named '_lock' is looked for (this attribute is expected to be
    the rw-lock object) in the instance object this decorator is attached to.
    """

    def decorator(f):
        attr_name = kwargs.get('lock', '_lock')

        @six.wraps(f)
        def wrapper(self, *args, **kwargs):
            rw_lock = getattr(self, attr_name)
            with rw_lock.write_lock():
                return f(self, *args, **kwargs)

        return wrapper

    # This is needed to handle when the decorator has args or the decorator
    # doesn't have args, python is rather weird here...
    if kwargs or not args:
        return decorator
    else:
        if len(args) == 1:
            return decorator(args[0])
        else:
            return decorator


class ReaderWriterLock(object):
    """A reader/writer lock.

    This lock allows for simultaneous readers to exist but only one writer
    to exist for use-cases where it is useful to have such types of locks.

    Currently a reader can not escalate its read lock to a write lock and
    a writer can not acquire a read lock while it is waiting on the write
    lock.

    In the future these restrictions may be relaxed.

    This can be eventually removed if http://bugs.python.org/issue8800 ever
    gets accepted into the python standard threading library...
    """
    WRITER = 'w'
    READER = 'r'

    @staticmethod
    def _fetch_current_thread_functor():
        # Until https://github.com/eventlet/eventlet/issues/172 is resolved
        # or addressed we have to use complicated workaround to get a object
        # that will not be recycled; the usage of threading.current_thread()
        # doesn't appear to currently be monkey patched and therefore isn't
        # reliable to use (and breaks badly when used as all threads share
        # the same current_thread() object)...
        if eventlet is not None and eventlet_patcher is not None:
            if eventlet_patcher.is_monkey_patched('thread'):
                return lambda: eventlet.getcurrent()
        return lambda: threading.current_thread()

    def __init__(self):
        self._writer = None
        self._pending_writers = collections.deque()
        self._readers = collections.deque()
        self._cond = threading.Condition()
        self._current_thread = self._fetch_current_thread_functor()

    @property
    def has_pending_writers(self):
        """Returns if there are writers waiting to become the *one* writer."""
        return bool(self._pending_writers)

    def is_writer(self, check_pending=True):
        """Returns if the caller is the active writer or a pending writer."""
        me = self._current_thread()
        if self._writer == me:
            return True
        if check_pending:
            return me in self._pending_writers
        else:
            return False

    @property
    def owner(self):
        """Returns whether the lock is locked by a writer or reader."""
        with self._cond:
            # Obtain the lock to ensure we get a accurate view of the actual
            # owner that isn't likely to change when we are reading it...
            if self._writer is not None:
                return self.WRITER
            if self._readers:
                return self.READER
            return None

    def is_reader(self):
        """Returns if the caller is one of the readers."""
        me = self._current_thread()
        return me in self._readers

    @contextlib.contextmanager
    def read_lock(self):
        """Context manager that grants a read lock.

        Will wait until no active or pending writers.

        Raises a RuntimeError if a pending writer tries to acquire
        a read lock.
        """
        me = self._current_thread()
        if me in self._pending_writers:
            raise RuntimeError("Writer %s can not acquire a read lock"
                               " while waiting for the write lock"
                               % me)
        with self._cond:
            while True:
                # No active writer, or we are the writer;
                # we are good to become a reader.
                if self._writer is None or self._writer == me:
                    self._readers.append(me)
                    break
                # An active writer; guess we have to wait.
                self._cond.wait()
        try:
            yield self
        finally:
            # I am no longer a reader, remove *one* occurrence of myself.
            # If the current thread acquired two read locks, then it will
            # still have to remove that other read lock; this allows for
            # basic reentrancy to be possible.
            with self._cond:
                self._readers.remove(me)
                self._cond.notify_all()

    @contextlib.contextmanager
    def write_lock(self):
        """Context manager that grants a write lock.

        Will wait until no active readers. Blocks readers after acquiring.

        Raises a RuntimeError if an active reader attempts to acquire a lock.
        """
        me = self._current_thread()
        if self.is_reader():
            raise RuntimeError("Reader %s to writer privilege"
                               " escalation not allowed" % me)
        if self.is_writer(check_pending=False):
            # Already the writer; this allows for basic reentrancy.
            yield self
        else:
            with self._cond:
                self._pending_writers.append(me)
                while True:
                    # No readers, and no active writer, am I next??
                    if len(self._readers) == 0 and self._writer is None:
                        if self._pending_writers[0] == me:
                            self._writer = self._pending_writers.popleft()
                            break
                    self._cond.wait()
            try:
                yield self
            finally:
                with self._cond:
                    self._writer = None
                    self._cond.notify_all()
