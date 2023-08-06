# -*- coding: utf-8 -*-

# --------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2015 Jonathan Labéjof <jonathan.labejof@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# --------------------------------------------------------------------

"""
Decorators dedicated to asynchronous programming.
"""

try:
    from threading import Thread, RLock
except ImportError as IE:
    from dummythreading import Thread, RLock

from time import sleep

try:
    from Queue import Queue
except ImportError:
    from queue import Queue

from signal import signal, SIGALRM, alarm

from b3j0f.annotation.interception import PrivateInterceptor
from b3j0f.annotation import Annotation
from b3j0f.annotation.oop import Mixin


class Synchronized(PrivateInterceptor):
    """
    Transform a target into a thread safe target.
    """

    #: lock attribute name
    _LOCK = '_lock'

    __slots__ = (_LOCK,) + PrivateInterceptor.__slots__

    def __init__(self, lock=None, *args, **kwargs):

        super(Synchronized, self).__init__(*args, **kwargs)

        self._lock = RLock() if lock is None else lock

    def _interception(self, annotation, advicesexecutor):

        self._lock.acquire()

        result = advicesexecutor.execute()

        self._lock.release()

        return result


class SynchronizedClass(Synchronized):
    """
    Transform a class into a thread safe class.
    """

    def on_bind_target(self, target):

        for attribute in target.__dict__:
            if callable(attribute):
                Synchronized(attribute, self._lock)


class Asynchronous(Annotation):
    """
    Transform a target into an asynchronous callable target.
    """

    def threaded(self, *args, **kwargs):

        result = self.__wraps(args, kwargs)
        self.queue.put(result)

    def on_bind_target(self, target):

        # add start function to wrapper
        super(Asynchronous, self).on_bind_target(target)

        setattr(target, 'start', self.start)

    def start(self, *args, **kwargs):

        self.queue = Queue()
        thread = Thread(target=self.threaded, args=args, kwargs=kwargs)
        thread.start()

        return Asynchronous.Result(self.queue, thread)

    class NotYetDoneException(Exception):

        pass

    class Result(object):

        __slots__ = ('queue', 'thread')

        def __init__(self, queue, thread):

            super(Asynchronous.Result, self).__init__()

            self.queue = queue
            self.thread = thread

        def is_done(self):

            return not self.thread.is_alive()

        def get_result(self, wait=-1):

            if not self.is_done():
                if wait >= 0:
                    self.thread.join(wait)
                else:
                    raise Asynchronous.NotYetDoneException(
                        'the call has not yet completed its task')

            if not hasattr(self, 'result'):
                self.result = self.queue.get()

            return self.result


class TimeOut(PrivateInterceptor):
    """
    Raise an Exception if the target call has not finished in time.
    """

    class TimeOutError(Exception):
        """
        Exception thrown if time elapsed before the end of the target call.
        """

        """
        Default time out error message.
        """
        DEFAULT_MESSAGE = \
            'Call of {0} with parameters {1} and {2} is timed out'

        def __init__(self, timeout_interceptor, frame):

            super(TimeOut.TimeOutError, self).__init__(
                timeout_interceptor.message.format(
                    timeout_interceptor.target,
                    timeout_interceptor.args,
                    timeout_interceptor.kwargs)
            )

    SECONDS = 'seconds'
    ERROR_MESSAGE = 'error_message'

    __slots__ = (SECONDS, ERROR_MESSAGE) + PrivateInterceptor.__slots__

    def __init__(
        self,
        seconds, error_message=TimeOutError.DEFAULT_MESSAGE,
        *args, **kwargs
    ):

        super(TimeOut, self).__init__(*args, **kwargs)

        self.seconds = seconds
        self.error_message = error_message

    def _handle_timeout(self, signum, frame):

        raise TimeOut.TimeOutError(self)

    def _interception(self, advicesexecutor):

        signal(SIGALRM, self._handle_timeout)
        alarm(self.seconds)
        try:
            result = advicesexecutor.execute()
        finally:
            signal.alarm(0)

        return result


class Wait(PrivateInterceptor):
    """
    Define a time to wait before and after a target call.
    """

    DEFAULT_WAIT = 1

    #: before attribute name
    BEFORE = 'before'

    #: after attribute name
    AFTER = 'after'

    __slots__ = (BEFORE, AFTER) + PrivateInterceptor.__slots__

    def __init__(
        self, before=DEFAULT_WAIT, after=DEFAULT_WAIT, *args, **kwargs
    ):

        super(Wait, self).__init__(*args, **kwargs)

        self.before = before
        self.after = after

    def _interception(self, advicesexecutor):

        sleep(self.before)

        result = advicesexecutor.execute()

        sleep(self._after_seconds)

        return result


class Observable(PrivateInterceptor):
    """
    Imlementation of the observer design pattern.
    It transforms a target into an observable object in adding method
    registerObserver, unregisterObserver and notify_observers.
    Observers listen to pre/post target interception.
    """

    def __init__(self):
        self._super(Observable).__init__()
        self.observers = set()

    def registerObserver(self, observer):
        """
        Register an observer.
        """

        self.observers.add(observer)

    def unregisterObserver(self, observer):
        """
        Unregister an observer.
        """

        self.observers.remove(observer)

    def notify_observers(self, target, args, kwargs, result=None, post=False):
        """
        Notify observers with parameter calls and information about
        pre/post call.
        """

        _observers = tuple(self.observers)

        for observer in _observers:
            observer.notify(target, args, kwargs, result, post)

    def on_bind_target(self, target):
        Mixin.set_mixin(target, self.registerObserver)
        Mixin.set_mixin(target, self.unregisterObserver)
        Mixin.set_mixin(target, self.notify_observers)

    def _pre_intercepts(self, target, args, kwargs):
        self._super(Observable)._pre_intercepts(target, args, kwargs)
        self.notify_observers(target, args, kwargs)

    def _post_intercepts(self, target, args, kwargs, result):
        self._super(Observable)._post_intercepts(target, args, kwargs)
        self.notify_observers(target, args, kwargs, result, post=True)
