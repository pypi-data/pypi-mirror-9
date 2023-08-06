# Copyright 2013-2014 Oliver Cope
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import sys

from .exceptions import ValidationError


__all__ = ('fail', 'assert_true', 'assert_false', 'maxlen', 'minlen',
           'gt', 'lt', 'gte', 'lte', 'matches', 'is_email', 'is_luhn_valid',
           'maxwords', 'minwords', 'eq', 'notempty', 'is_in')

if sys.version_info[0] == 2:
    _strtypes = basestring
else:
    _strtypes = (str, bytes)


def fail(message=None):
    raise ValidationError(message)


def assert_true(predicate, message):
    """
    Raise a ``ValidationError`` if ``predicate`` is not ``True``
    """
    if not predicate:
        raise ValidationError(message)
    return True


def assert_false(predicate, message):
    """
    Raise a ``ValidationError`` if ``predicate`` is not ``False``
    """
    if predicate:
        raise ValidationError(message)
    return True


def minlen(l, message=None):
    return lambda v: assert_true(len(v) >= l, message)


def maxlen(l, message=None):
    return lambda v: assert_true(len(v) <= l, message)


def gt(l, message=None):
    return lambda v: assert_true(v > l, message)


def gte(l, message=None):
    return lambda v: assert_true(v >= l, message)


def lt(l, message=None):
    return lambda v: assert_true(v < l, message)


def lte(l, message=None):
    return lambda v: assert_true(v <= l, message)


def matches(p, message=None):
    if isinstance(p, _strtypes):
        p = re.compile(p)
    return lambda v: assert_true(p.search(v) is not None, message)


def notempty(message=None):
    return matches(re.compile(r'\S'), message)


def eq(expected, message=None):
    return lambda v: assert_true(v == expected, message)


def is_in(allowed, message=None):
    return lambda v: assert_true(v in allowed, message)


def is_email(message="Enter a valid email address",
             _match=re.compile(r'^\S+@\S+\.\S+$').match):
    """
    Check that the value is superficially like an email address, ie that it
    contains a local part and domain, separated with an ``@``.

    Beyond this it is difficult to verify an email address (and technically
    valid RFC2822 email addresses may still break your application code - the
    range of what counts as valid is notoriously wide). The only way to know
    for sure is for your application to send a confirmation email to the
    address.
    """
    return lambda v: assert_true(_match(v) is not None, message)


def maxwords(n, message="Value is too long",
             _split=re.compile(r'\S+').finditer):
    """
    Check that the value has no more than ``n`` words
    """
    # Enumerate starts counting at 0
    n = n - 1
    return lambda v: assert_true(
                        all(i <= n for i, _ in enumerate(_split(v))), message)


def minwords(n, message="Value is too long",
             _split=re.compile(r'\S+').finditer):
    """
    Check that the value has at least ``n`` words
    """
    # Enumerate starts counting at 0
    n = n - 1
    return lambda v: assert_true(
                        any(i >= n for i, _ in enumerate(_split(v))), message)


def is_luhn_valid(message="Enter a valid card number"):
    """
    Check that a credit card number passes the Lunh checksum algorithm
    """
    def is_luhn_valid(cc):
        import string
        digits = [int(x) for x in cc if x in string.digits]
        result = sum(digits[::-2] +
                     [sum(divmod(d * 2, 10)) for d in digits[-2::-2]]) % 10
        return assert_true(result == 0, message)
    return is_luhn_valid
