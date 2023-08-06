#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#
from fresco.cookie import Cookie


class TestCookie(object):

    def test_basic_cookie(self):
        """Simple cookie with just a field and value"""
        c = Cookie('key', 'value')
        assert str(c) == 'key=value'

    def test_httponly_cookie(self):
        """Cookie as HttpOnly"""
        c = Cookie('key', 'value', httponly=True)
        assert str(c) == 'key=value;HttpOnly'

    def test_secure_cookie(self):
        """Cookie as secure cookie"""
        c = Cookie('key', 'value', secure=True)
        assert str(c) == 'key=value;Secure'

    def test_secure_and_httponly(self):
        """Cookie as both secure and httponly"""
        c = Cookie('key', 'value', secure=True, httponly=True)
        assert str(c) == 'key=value;Secure;HttpOnly'
