# -*- coding: utf-8 -*-
"""
test_utils
~~~~~~~~~~

Test miscellaneous utility functions.

:copyright: Copyright 2014 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
import datetime
import logging

import nose
from nose.tools import eq_, ok_

from chemspipy.utils import timestamp, duration


logging.basicConfig(level=logging.WARN, format='%(levelname)s:%(name)s:(%(threadName)-10s):%(message)s')
logging.getLogger('chemspipy').setLevel(logging.DEBUG)


def test_timestamp_microseconds():
    """Test timestamp parser function on timestamps strings with microseconds."""
    eq_(timestamp('2007-08-08T20:18:36.593'), datetime.datetime(2007, 8, 8, 20, 18, 36, 593000))
    eq_(timestamp('2035-12-31T23:59:59.999'), datetime.datetime(2035, 12, 31, 23, 59, 59, 999000))


def test_timestamp_seconds():
    """Test timestamp parser function on timestamps strings with no microseconds."""
    eq_(timestamp('2007-08-08T20:18:36'), datetime.datetime(2007, 8, 8, 20, 18, 36))
    eq_(timestamp('2010-09-01T04:33:59'), datetime.datetime(2010, 9, 1, 4, 33, 59))


def test_duration_microseconds():
    """Test duration parser function on duration strings with microseconds."""
    eq_(duration('0:00:00.001'), datetime.timedelta(0, 0, 1000))
    eq_(duration('0:00:00.12'), datetime.timedelta(0, 0, 120000))
    eq_(duration('0:00:00.120'), datetime.timedelta(0, 0, 120000))
    eq_(duration('0:00:00.052'), datetime.timedelta(0, 0, 52000))
    eq_(duration('0:00:03.523'), datetime.timedelta(0, 3, 523000))


def test_duration_seconds():
    """Test duration parser function on duration strings with no microseconds."""
    eq_(duration('0:00:00'), datetime.timedelta(0))
    eq_(duration('0:00:03'), datetime.timedelta(0, 3))


if __name__ == '__main__':
    nose.main()
