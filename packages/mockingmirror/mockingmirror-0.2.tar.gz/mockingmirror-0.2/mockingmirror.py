# Copyright 2015 Mark Haines
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import mock
from functools import wraps

__version__ = "0.2"


def mirror():
    """Returns a tuple of a mirror and the mock object that it configures"""
    mirror = Mirror()
    return (mirror, mirror._mock)


def mirrored(setup):
    """Convience decorator for setUp in testcases::

        @mirrored
        def setUp(self, mirror, mock):
            ...

    is the same as::

        def setUp(self):
            self.mirror, self.mock = mirror()
            mirror, mock = self.mirror, self.mock
            ...
    """
    @wraps(setup)
    def wrapped_setup(self):
        self.mirror, self.mock = mirror()
        return setup(self, self.mirror, self.mock)
    return wrapped_setup


class NonCallableMock(mock.NonCallableMock):
    def __getattr__(self, name):
        try:
            return super(NonCallableMock, self).__getattr__(name)
        except AttributeError:
            raise AttributeError("%r has no attribute %r" % (self, name))


class Mirror(object):
    """Convienence object for setting up mock objects::

        mirror.myobject.mymethod()[:] = "Hello"

    does the same as::

        mock.myobject = NonCallableMock(spec_set=["mymethod"])
        mock.myobject.mymethod = Mock(spec_set=[])
        mock.myobject.mymethod.return_value = "Hello"

    """

    def __init__(self, name=None, parent=None, mirrors=None):
        if mirrors is None:
            mirrors = []
        if parent is not None and parent._name is not None:
            path = parent._name + "." + name
        else:
            path = name
        # Add a temporary mock to capture all of the following calls to setattr
        self._mock = mock.NonCallableMock()
        self._spec = set()
        self._name = name
        self._parent = parent
        self._mirrors = mirrors
        self._mirrors.append(self)
        self._is_callable = False
        self._path = path
        # Replace our mock and spec objects.
        self._mock = NonCallableMock(name=path)
        self._mock.mock_add_spec([], True)
        self._spec = set()
        if name is not None:
            setattr(self._parent._mock, self._name, self._mock)

    def __getattr__(self, name):
        """Whenever a member or method is accessed on the mirror for the
        first time we need to create a new mirror for that potential member
        or method."""
        self._add_to_spec(name)
        mirror = Mirror(name, self, self._mirrors)
        object.__setattr__(self, name, mirror)
        return mirror

    def __setattr__(self, name, value):
        """Setting an attribute on the mirror causes the same attribute to be
        set on the mock object it is mirroring."""
        object.__setattr__(self, name, value)
        if name != "_mock" and name != "_spec":
            self._add_to_spec(name)
            setattr(self._mock, name, value)

    def __call__(self):
        """Calling a mirror makes the mirrored mock object callable.
        Returns an invocation object that can be used to set return values and
        side effects for the mocked method."""
        if not self._is_callable:
            self._is_callable = True
            self._mock = mock.Mock(name=self._path)
            self._mock.add_spec([], True)
            setattr(self._parent._mock, self._name, self._mock)
        return Invocation(self, self._mock)

    def _add_to_spec(self, name):
        """The spec of the mirrored mock object is updated whenever the mirror
        gains new attributes"""
        self._spec.add(name)
        self._mock.mock_add_spec(list(self._spec), True)


class ReturnValueNotSet(object):
    """Special object to indicate methods without return values"""
    __slots__ = []

    def __repr__(self):
        return "RETURN_VALUE_NOT_SET"

RETURN_VALUE_NOT_SET = ReturnValueNotSet()


class Invocation(object):
    """Used to manipulate the return value and side effects of mock methods"""
    def __init__(self, mirror, mock):
        self.mirror = mirror
        self.mock = mock
        self.mock.return_value = RETURN_VALUE_NOT_SET

    def __call__(self, side_effect):
        """Decorate a function to use it as a side effect"""
        self.mock.side_effect = side_effect

    def __setitem__(self, _ignored, return_value):
        """Item assignment sets the return value and removes any side effect"""
        self.mock.return_value = return_value
        self.mock.side_effect = None
