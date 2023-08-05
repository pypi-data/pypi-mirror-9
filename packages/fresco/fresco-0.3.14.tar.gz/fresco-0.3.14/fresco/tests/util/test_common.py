from __future__ import absolute_import

from fresco.util.common import object_or_404
from fresco.exceptions import NotFound
import pytest


class TestObjectOr404(object):

    def test_it_returns_the_object(self):
        ob = object()
        assert object_or_404(ob) is ob

    def test_it_raises_NotFound(self):
        with pytest.raises(NotFound):
            object_or_404(None)

    def test_it_raises_custom_exception(self):
        class Foo(Exception):
            pass
        with pytest.raises(Foo):
            object_or_404(None, exception=Foo)
