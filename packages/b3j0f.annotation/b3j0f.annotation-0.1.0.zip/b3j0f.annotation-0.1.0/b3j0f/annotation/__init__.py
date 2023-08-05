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

"""This module defines the Annotation class.

Such Annotation is close to the reflective paradigm in having himself its own
    lifecycle independently from its annotated elements (called commonly
        target).

Such Annotation:

- can annotate all python object, from classes to class instances.
- have their own business behaviour.
- are reusable to annotate several objects.
- can propagate their annotation capability to class inheritance tree.

.. limitations:
    It is impossible to annotate None methods.
"""

__version__ = "0.1.0"

__all__ = ['Annotation', 'StopPropagation', 'RoutineAnnotation']

from b3j0f.utils.property import (
    put_properties, del_properties, get_local_property, get_property
)

from time import time

try:
    from threading import Timer
except ImportError:
    from dummy_threading import Timer


class Annotation(object):
    """Base class for all annotations defined in this library.

    It contains functions to override in order to catch initialisation
    of this Annotation and annotated elements binding
    (also called commonly target in the context of Annotation).

    All annotations which inherit from this are registered to target objects
    and are accessibles through the static method Annotation.get_annotations.

    Instance methods to override are:
    - __init__: set parameters during its instantiation.
    - _bind_target: called to bind target to this.
    - on_bind_target: fired when the annotated element is bound to this.

    And properties are:
    - propagate: (default True) determines if an annotation is propagated to
        all sub target elements.
    - override: (default False) exclude previous annotation of the same type as
        self class.
    - ttl: (default None) self time to leave.
    - in_memory: (default False) save instance in a global dictionary.

    It is also possible to set on_bind_target, propagate and override in
        the constructor.
    """

    #: attribute name for accessing to target annotations from a target
    __ANNOTATIONS_KEY__ = '__ANNOTATIONS__'

    #: attribute name for target binding notifying
    _ON_BIND_TARGET = '_on_bind_target'

    #: atribute name for target
    TARGETS = 'targets'

    #: attribute name for annotation propagatation on sub targets.
    PROPAGATE = 'propagate'

    #: attribute name for overriding base annotations.
    OVERRIDE = 'override'

    #: attribute name for annotation ttl
    TTL = 'ttl'

    #: attribute name for in_memory
    IN_MEMORY = 'in_memory'

    #: attribute name for self ts
    __TS = '_ts'

    #: attribute name for self timer
    __TIMER = '_timer'

    __slots__ = (
        _ON_BIND_TARGET, __TS, __TIMER,  # private attributes
        TARGETS, PROPAGATE, OVERRIDE, TTL, IN_MEMORY  # public attributes
    )

    # global dictionary of annotations in memory
    __ANNOTATIONS_IN_MEMORY__ = {}

    def __init__(
        self,
        on_bind_target=None, propagate=True, override=False, ttl=None,
        in_memory=False
    ):
        """Default constructor with an 'on_bind_target' handler and propagate
        scope property.

        :param on_bind_target: (None) function to call when the annotation is
            bound to an object. Function parameters are self and target.
        :param bool propagate: (True) propagate self to sub targets.
        :param bool override: (False) override old defined annotations of the
            same type.
        :param float ttl: (None) self ttl in seconds.
        :param bool in_memory: (False) save self in a global memory.
        """

        super(Annotation, self).__init__()

        # set on_bind_target handler
        setattr(self, Annotation._ON_BIND_TARGET, on_bind_target)

        # set attributes
        setattr(self, Annotation.PROPAGATE, propagate)
        setattr(self, Annotation.OVERRIDE, override)
        setattr(self, Annotation.TTL, ttl)
        setattr(self, Annotation.IN_MEMORY, in_memory)

        self.targets = set()

    def __call__(self, target, ctx=None):
        """Shouldn't be overriden by sub classes.

        :param target: target to annotate.
        :param ctx: target ctx.
        :return: annotated element.
        """

        # bind target to self
        result = self.bind_target(target=target, ctx=ctx)

        return result

    def __del__(self):
        """Remove self to self.target annotations.
        """

        try:
            # nonify self ttl
            setattr(self, Annotation.TTL, None)

            # for all target
            for target in tuple(self.targets):
                # remove self from target
                try:
                    self.remove_from(target)
                except TypeError:
                    # raised if target is not hashable
                    pass

            # remove self from memory
            setattr(self, Annotation.IN_MEMORY, False)
        except AttributeError:
            # raised if self is deleted during __del__ execution
            pass

    @property
    def ttl(self):
        """Get actual ttl in seconds.

        :return: actual ttl
        :rtype: float
        """

        # result is self ts
        result = getattr(self, Annotation.__TS, None)
        # if result is not None
        if result is not None:
            # result is now - result
            now = time()
            result = result - now

        return result

    @ttl.setter
    def ttl(self, value):
        """Change self ttl with input value.

        :param float value: new ttl in seconds
        """

        # get timer
        timer = getattr(self, Annotation.__TIMER, None)
        # if timer is running, stop the timer
        if timer is not None:
            timer.cancel()
        # initialize timestamp
        ts = None

        # if value is None
        if value is None:
            # nonify timer
            timer = None

        else:  # else, renew a timer
            # get ts
            ts = time() + value
            # start a new timer
            timer = Timer(value, self.__del__)
            timer.start()
            # set/update attributes

        setattr(self, Annotation.__TIMER, timer)
        setattr(self, Annotation.__TS, ts)

    @property
    def in_memory(self):
        """
        :return: True if self is in a global memory of annotations.
        """

        self_class = self.__class__
        # check if self class is in global memory
        memory = Annotation.__ANNOTATIONS_IN_MEMORY__.get(self_class, ())
        # check if self is in memory
        result = self in memory

        return result

    @in_memory.setter
    def in_memory(self, value):
        """Add or remove self from global memory.

        :param bool value: if True(False) ensure self is(is not) in memory
        """

        self_class = self.__class__
        memory = Annotation.__ANNOTATIONS_IN_MEMORY__
        if value:
            annotations_memory = memory.setdefault(self_class, set())
            annotations_memory.add(self)
        else:
            if self_class in memory:
                annotations_memory = memory[self_class]
                while self in annotations_memory:
                    annotations_memory.remove(self)
                if not annotations_memory:
                    del memory[self_class]

    def bind_target(self, target, ctx=None):
        """Bind self annotation to target.

        :param target: target to annotate.
        :param ctx: target ctx.
        :return: bound target.
        """

        # process self _bind_target
        result = self._bind_target(target=target, ctx=ctx)

        # fire on bind target event
        self.on_bind_target(target=target, ctx=ctx)

        return result

    def _bind_target(self, target, ctx=None):
        """Method to override in order to specialize binding of target.

        :param target: target to bind
        :param ctx: target ctx.
        :return: bound target.
        """

        result = target

        try:
            # get annotations from target if exists.
            local_annotations = get_local_property(
                target, Annotation.__ANNOTATIONS_KEY__, []
            )
        except TypeError:
            raise TypeError('target {0} must be hashable.'.format(target))

        # if local_annotations do not exist, put them in target
        if not local_annotations:
            put_properties(
                target,
                properties={Annotation.__ANNOTATIONS_KEY__: local_annotations}
            )

        # insert self at first position
        local_annotations.insert(0, self)

        # add target to self targets
        self.targets.add(target)

        return result

    def on_bind_target(self, target, ctx=None):
        """Fired after target is bound to self.

        :param target: newly bound target.
        :param ctx: target ctx.
        """

        _on_bind_target = getattr(self, Annotation._ON_BIND_TARGET, None)

        if _on_bind_target is not None:
            _on_bind_target(self, target=target, ctx=ctx)

    def remove_from(self, target, ctx=None):
        """Remove self annotation from target annotations.

        :param target: target from where remove self annotation.
        :param ctx: target ctx.
        """

        annotations_key = Annotation.__ANNOTATIONS_KEY__

        try:
            # get local annotations
            local_annotations = get_local_property(target, annotations_key)
        except TypeError:
            raise TypeError('target {0} must be hashable'.format(target))

        # if local annotations exist
        if local_annotations is not None:
            # if target in self.targets
            if target in self.targets:
                # remove target from self.targets
                self.targets.remove(target)
                # and remove all self annotations from local_annotations
                while self in local_annotations:
                    local_annotations.remove(self)
                # if target is not annotated anymore, remove the empty list
                if not local_annotations:
                    del_properties(target, annotations_key)

    @classmethod
    def free_memory(annotation_type, exclude=None):
        """Free global annotation memory.
        """

        annotations_in_memory = Annotation.__ANNOTATIONS_IN_MEMORY__

        exclude = () if exclude is None else exclude

        for annotation_cls in annotations_in_memory.keys():

            if issubclass(annotation_cls, exclude):
                continue

            if issubclass(annotation_cls, annotation_type):
                del annotations_in_memory[annotation_cls]

    @classmethod
    def get_memory_annotations(annotation_type, exclude=None):
        """Get annotations in memory which inherits from annotation_type.

        :param tuple/type exclude: annotation type(s) to exclude from search
        :return: found annotations which inherits from annotation_type.
        :rtype: set
        """

        result = set()

        # get global dictionary
        annotations_in_memory = Annotation.__ANNOTATIONS_IN_MEMORY__

        exclude = () if exclude is None else exclude

        # iterate on annotation classes
        for annotation_cls in annotations_in_memory:

            # if annotation class is excluded, continue
            if issubclass(annotation_cls, exclude):
                continue

            # if annotation class inherits from self, add it in the result
            if issubclass(annotation_cls, annotation_type):
                result |= annotations_in_memory[annotation_cls]

        return result

    @classmethod
    def get_local_annotations(annotation_type, target, exclude=None, ctx=None):
        """Get a list of local target annotations in the order of their
            definition.

        :param type annotation_type: type of annotation to get from target.
        :param target: target from where get annotations.
        :param tuple/type exclude: annotation types to exclude from selection.
        :param ctx: target ctx.

        :return: target local annotations
        :rtype: list
        """

        result = []

        # initialize exclude
        exclude = () if exclude is None else exclude

        try:
            # get local annotations
            local_annotations = get_local_property(
                target, Annotation.__ANNOTATIONS_KEY__, result
            )
        except TypeError:
            raise TypeError('target {0} must be hashable'.format(target))

        for local_annotation in local_annotations:
            # check if local annotation inherits from annotation_type
            inherited = isinstance(local_annotation, annotation_type)
            # and if not excluded
            not_excluded = not isinstance(local_annotation, exclude)

            # if both conditions, add local annotation to the result
            if inherited and not_excluded:
                result.append(local_annotation)

        return result

    @classmethod
    def remove(annotation_type, target, exclude=None, ctx=None):
        """Remove from target annotations which inherit from annotation_type

        :param target: target from where remove annotations which inherits from
            annotation_type.
        :param tuple/type exclude: annotation types to exclude from selection.
        :param ctx: target ctx.
        """

        # initialize exclude
        exclude = () if exclude is None else exclude

        try:
            # get local annotations
            local_annotations = get_local_property(
                target, Annotation.__ANNOTATIONS_KEY__
            )
        except TypeError:
            raise TypeError('target {0} must be hashable'.format(target))

        # if there are local annotations
        if local_annotations is not None:

            # get annotations to remove which inherits from annotation_type
            annotations_to_remove = [
                annotation for annotation in local_annotations
                if isinstance(annotation, annotation_type)
                    and not isinstance(annotation, exclude)
            ]

            # and remove annotations from target
            for annotation_to_remove in annotations_to_remove:
                annotation_to_remove.remove_from(target)

    @classmethod
    def get_annotations(annotation_type, target, exclude=None, ctx=None):
        """Returns all input target annotations of annotation_type type sorted
        by definition order.

        :param type annotation_type: type of annotation to get from target.
        :param target: target from where get annotations.
        :param tuple/type exclude: annotation types to remove from selection.
        :param ctx: target ctx.
        """

        result = []

        annotations_by_ctx = get_property(
            elt=target, key=Annotation.__ANNOTATIONS_KEY__, ctx=ctx
        )

        exclude = () if exclude is None else exclude

        for elt, annotations in annotations_by_ctx:

            for annotation in annotations:

                # check if annotation is a StopPropagation rule
                if isinstance(annotation, StopPropagation):
                    exclude += annotation.annotation_types

                # ensure propagation
                if elt is not target and not annotation.propagate:
                    continue

                # ensure overriding
                if annotation.override:
                    exclude += (annotation.__class__, )

                # check for annotation type
                if (isinstance(annotation, annotation_type)
                        and not isinstance(annotation, exclude)):

                    result.append(annotation)

        return result

    @classmethod
    def get_annotated_fields(annotation_type, instance):
        """Get arrays of (annotated fields, annotations) by annotation_type of
            input instance.

        :return: a set of (annotated fields, annotations)
        :rtype: dict
        """

        result = {}

        field_names = dir(instance)

        for field_name in field_names:
            field = getattr(instance, field_name)
            try:
                annotations = annotation_type.get_annotations(field)
            except TypeError:
                continue
            if annotations:
                result[field] = annotations

        return result


class StopPropagation(Annotation):
    """Stop propagation for annotation types.
    """

    ANNOTATION_TYPES = 'annotation_types'

    __slots__ = (ANNOTATION_TYPES,) + Annotation.__slots__

    def __init__(self, *annotation_types, **kwargs):
        """Define annotation types to not propagate at this level.
        """

        super(StopPropagation, self).__init__(**kwargs)

        setattr(self, StopPropagation.ANNOTATION_TYPES, annotation_types)


class RoutineAnnotation(Annotation):
    """Dedicated to add information on any routine, routine parameters or
    routine result.
    """

    #: routine attribute name
    ROUTINE = 'routine'

    #: result attribute name
    RESULT = 'result'

    #: parameters attribute name
    PARAMS = 'params'

    __slots__ = (ROUTINE, RESULT, PARAMS) + Annotation.__slots__

    def __init__(
        self, routine=None, params=None, result=None, *args, **kwargs
    ):
        """
        :param routine: routine information
        :param params: params information
        :param result: routine result information
        """

        super(RoutineAnnotation, self).__init__(*args, **kwargs)

        setattr(self, RoutineAnnotation.ROUTINE, routine)
        setattr(self, RoutineAnnotation.PARAMS, params)
        setattr(self, RoutineAnnotation.RESULT, result)
