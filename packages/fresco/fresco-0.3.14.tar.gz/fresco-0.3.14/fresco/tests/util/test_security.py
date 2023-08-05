from __future__ import absolute_import

import pytest

from fresco.util import security


class TestSecurity(object):

    def test_check_equal_constant_time_returns_equality(self):
        assert security.check_equal_constant_time('', '') is True
        assert security.check_equal_constant_time('abcabcabc', 'abcabcabc') \
                is True

    def test_check_equal_constant_time_returns_inequality(self):
        assert security.check_equal_constant_time(' ', '') is False
        assert security.check_equal_constant_time('abcabcabc', 'abcabcabx') \
                is False
        assert security.check_equal_constant_time('abcabcabc', 'abcabcabx') \
                is False
        assert security.check_equal_constant_time('abcabcabc', 'abcabcabde') \
                is False
        assert security.check_equal_constant_time('abcabcabc', 'abcabcab') \
                is False

    def test_check_equal_constant_time_raises_an_error_on_non_strings(self):
        with pytest.raises(TypeError):
            security.check_equal_constant_time(None, None)
