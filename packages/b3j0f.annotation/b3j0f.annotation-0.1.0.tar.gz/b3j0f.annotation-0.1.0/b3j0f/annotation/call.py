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
Decorators dedicated to class or functions calls.
"""

from b3j0f.annotation.interception import PrivateInterceptor
from b3j0f.annotation.check import Target
from b3j0f.utils.iterable import first

try:
    from inspect import getcallargs
except ImportError:
    from b3j0f.utils.version import getcallargs

from sys import stderr

from time import sleep

from functools import wraps

__all__ = [
    'Types', 'types', 'Curried', 'curried', 'Retries'
]


@Target(callable)
class Types(PrivateInterceptor):
    """
    Check routine parameters and return type.
    """

    class TypesError(Exception):
        pass

    class _SpecialCondition(object):

        def __init__(self, _type):

            super(Types._SpecialCondition, self).__init__()

            self._type = _type

        def get_type(self):

            return self._type

    class NotNone(_SpecialCondition):
        pass

    class NotEmpty(_SpecialCondition):
        pass

    class _NamedParameterType(object):

        def __init__(self, name, parameter_type):

            super(Types._NamedParameterType, self).__init__()

            self._name = name
            self._parameter_type = parameter_type

    class _NamedParameterTypes(object):

        def __init__(self, target, named_parameter_types):

            super(Types._NamedParameterTypes, self).__init__()

            self._named_parameter_types = []

            for index in range(target.__code__.co_argcount):
                target_parameter_name = target.__code__.co_varnames[index]

                if target_parameter_name in named_parameter_types:
                    parameter_type = \
                        named_parameter_types[target_parameter_name]
                    named_parameter_type = \
                        Types._NamedParameterType(
                            target_parameter_name,
                            parameter_type)
                    self._named_parameter_types.append(named_parameter_type)

                else:
                    self._named_parameter_types.append(None)

    #: return type attribute name
    RTYPE = 'rtype'

    #: parameter types attribute name
    PTYPES = 'ptypes'

    __slots__ = (RTYPE, PTYPES) + PrivateInterceptor.__slots__

    """
    Check parameter or result types of decorated class or function call.
    """
    def __init__(self, rtype=None, ptypes=None, *args, **kwargs):
        """
        :param rtype:
        """

        super(Types, self).__init__(*args, **kwargs)

        self.rtype = rtype
        self.ptypes = {} if ptypes is None else ptypes

    @staticmethod
    def check_value(value, expected_type):

        result = False

        if isinstance(expected_type, Types.NotNone):
            result = value is not None and Types.check_value(
                value,
                expected_type.get_type())

        else:
            result = value is None

            if not result:

                value_type = type(value)

                if isinstance(expected_type, Types.NotEmpty):
                    try:
                        result = len(value) != 0
                        if result:
                            _type = expected_type.get_type()
                            result = Types.check_value(value, _type)
                    except TypeError:
                        result = False

                elif isinstance(expected_type, list):
                    result = issubclass(value_type, list)

                    if result:
                        if len(expected_type) == 0:
                            result = len(value) == 0
                        else:
                            _expected_type = expected_type[0]

                            for item in value:
                                result = Types.check_value(
                                    item,
                                    _expected_type)

                                if not result:
                                    break

                elif isinstance(expected_type, set):
                    result = issubclass(value_type, set)

                    if result:
                        if len(expected_type) == 0:
                            result = len(value) == 0
                        else:

                            _expected_type = expected_type.copy().pop()
                            _value = value.copy()

                            value_length = len(_value)

                            for count in range(value_length):
                                item = _value.pop()
                                result = Types.check_value(
                                    item,
                                    _expected_type)

                                if not result:
                                    break
                else:
                    result = issubclass(value_type, expected_type)

        return result

    def _interception(self, joinpoint):

        target = joinpoint.target
        args = joinpoint.args
        kwargs = joinpoint.kwargs

        if self.ptypes:
            callargs = getcallargs(target, *args, **kwargs)

            for arg in callargs:
                value = callargs[arg]
                expected_type = self.ptypes.get(arg)

                if expected_type is not None and \
                    not Types.check_value(
                        value,
                        expected_type):
                    raise Types.TypesError(
                        "wrong typed parameter for arg {0} : {1} ({2}). \
                        Expected: {3}.".format(
                        (arg, value, type(value), expected_type))
                    )

        result = joinpoint.proceed()

        target = joinpoint.target
        args = joinpoint.args
        kwargs = joinpoint.kwargs

        if self.rtype:
            if not Types.check_value(result, self.rtype):
                raise Types.TypesError(
                    "wrong result type for {0} with parameters {1}, {2}: {3} \
                    ({4}). Expected {5}.".
                    format(
                        target, args, kwargs, result, type(result),
                        self.rtype)
                )

        return result


def types(*args, **kwargs):
    """Quick alias for the Types Annotation with only args and kwargs
    parameters.

    args may contain rtype and kwargs is ptypes.
    """

    rtype = first(args)

    return Types(rtype=rtype, ptypes=kwargs)


class Curried(PrivateInterceptor):
    """Annotation that returns a function that keeps returning functions
    until all arguments are supplied; then the original function is
    evaluated.

    Inspirated from Jeff Laughlin Consulting LLC projects.
    """

    ARGS = 'args'  #: args attribute name
    KWARGS = 'kwargs'  #: kwargs attribute name
    DEFAULT_ARGS = 'default_args'  #: default args attribute name
    DEFAULT_KWARGS = 'default_kwargs'  #: default kwargs attribute name

    __slots__ = (
        ARGS, KWARGS, DEFAULT_ARGS, DEFAULT_KWARGS
    ) + PrivateInterceptor.__slots__

    class CurriedResult(object):
        """Curried result in case of missing arguments.
        """

        __slots__ = ('curried', 'exception')

        def __init__(self, curried, exception):

            super(Curried.CurriedResult, self).__init__()

            self.curried = curried
            self.exception = exception

    def __init__(self, varargs=(), keywords={}, *args, **kwargs):

        super(Curried, self).__init__(*args, **kwargs)

        self.args = self.default_args = varargs
        self.kwargs = self.default_kwargs = keywords

    def _bind_target(self, target, *args, **kwargs):

        @wraps(target)
        def f(*args, **kwargs):
            return target(*args, **kwargs)

        result = super(Curried, self)._bind_target(
            target=f, *args, **kwargs
        )

        return result

    def _interception(self, joinpoint, *args, **kwargs):

        result = None

        target = joinpoint.target

        args = joinpoint.args
        kwargs = joinpoint.kwargs

        self.kwargs.update(kwargs)
        self.args += args

        try:
            # check if all arguments are given
            getcallargs(target, *self.args, **self.kwargs)
            joinpoint.args = self.args
            joinpoint.kwargs = self.kwargs
            result = joinpoint.proceed()
        except TypeError as te:
            # in case of problem, returns curried decorater and exception
            result = Curried.CurriedResult(self, te)

        return result


def curried(*args, **kwargs):
    """Curried annotation with varargs and kwargs.
    """

    return Curried(varargs=args, keywords=kwargs)


def example_exc_handler(tries_remaining, exception, delay):
    """Example exception handler; prints a warning to stderr.

    tries_remaining: The number of tries remaining.
    exception: The exception instance which was raised.
    """

    print >> stderr, "Caught '{0}', {1} tries remaining, \
    sleeping for {2} seconds".format(exception, tries_remaining, delay)


class Retries(PrivateInterceptor):
    """Function decorator implementing retrying logic.

    delay: Sleep this many seconds * backoff * try number after failure
    backoff: Multiply delay by this factor after each failure
    exceptions: A tuple of exception classes; default (Exception,)
    hook: A function with the signature myhook(tries_remaining, exception);
          default None

    The decorator will call the function up to max_tries times if it raises
    an exception.

    By default it catches instances of the Exception class and subclasses.
    This will recover after all but the most fatal errors. You may specify a
    custom tuple of exception classes with the 'exceptions' argument; the
    function will only be retried if it raises one of the specified
    exceptions.

    Additionally you may specify a hook function which will be called prior
    to retrying with the number of remaining tries and the exception instance;
    see given example. This is primarily intended to give the opportunity to
    log the failure. Hook is not called after failure if no retries remain.
    """

    MAX_TRIES = 'max_tries'
    DELAY = 'delay'
    BACKOFF = 'backoff'
    EXCEPTIONS = 'exceptions'
    HOOK = 'hook'

    __slots__ = (
        MAX_TRIES, DELAY, BACKOFF, EXCEPTIONS, HOOK
    ) + PrivateInterceptor.__slots__

    def __init__(
        self,
        max_tries,
        delay=1,
        backoff=2,
        exceptions=(Exception,),
        hook=None,
        *args, **kwargs
    ):

        super(Retries, self).__init__(*args, **kwargs)

        self.max_tries = max_tries
        self.delay = delay
        self.backoff = backoff
        self.exceptions = exceptions
        self.hook = hook

    def _interception(self, joinpoint):

        result = None

        mydelay = self.delay
        tries = list(range(self.max_tries))
        tries.reverse()

        for tries_remaining in tries:

            try:
                result = joinpoint.proceed()

            except self.exceptions as e:

                if tries_remaining > 0:

                    if self.hook is not None:
                        self.hook(tries_remaining, e, mydelay)

                    sleep(mydelay)
                    mydelay = mydelay * self.backoff

                else:
                    raise
            else:
                break

        return result
