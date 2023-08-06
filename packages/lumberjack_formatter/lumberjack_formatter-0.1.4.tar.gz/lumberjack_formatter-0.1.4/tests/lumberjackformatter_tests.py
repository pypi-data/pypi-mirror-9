import time
import json
import logging

try:
    # >=3.3
    from unittest.mock import patch, sentinel
except ImportError:
    # <=3.2
    from mock import patch, sentinel

# >=2.7
from nose.tools import eq_

# 2.6 assert functions
try:
    from nose.tools import assert_in, assert_is_not_none
except ImportError:
    def assert_in(item, collection, msg = None):
        if msg is None:
            msg = '%r not in %r' % (item, collection)
        assert item in collection, msg

    def assert_is_not_none(item, msg = None):
        if msg is None:
            '%r not None' % item
        assert item is not None, msg

from lumberjack_formatter.formatter import LumberjackFormatter

import re

from mockpatchhelper import MockingTestCase

log = logging.getLogger('lumberjack_formatter.tests')

# noinspection PyUnresolvedReferences
class LumberjackFormatter_Tests(MockingTestCase):

    STANDARD_LOG_ATTRS = LumberjackFormatter.RESERVED_ATTRS

    ISO8601_PATTERN = re.compile('^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[0-1]|0[1-9]|[1-2][0-9])T(2[0-3]|[0-1][0-9]):([0-5][0-9]):([0-5][0-9])(\.([0-9]+))?(Z|[+-](?:2[0-3]|[0-1][0-9]):[0-5][0-9])?$')

    def setUp(self):
        # mock all the methods which will be used in testing
        self._patch(patch('time.time', return_value=time.mktime(time.localtime(0))+1e-06, autospec=True))

        extras = {'a': sentinel.a, 'b': sentinel.b}

        standards = dict((k, getattr(sentinel, k)) for k in self.STANDARD_LOG_ATTRS if k not in ('asctime','timestamp','message','msg',))
        standards['msg'] = standards['message'] = sentinel.anymessage

        mixed_items = extras.copy()
        mixed_items.update(standards)

        self.extras_rec = logging.makeLogRecord(extras)
        self.standard_rec = logging.makeLogRecord(standards)
        self.blank_rec = logging.makeLogRecord({})
        self.mixed_rec = logging.makeLogRecord(mixed_items)

    def tearDown(self):
        super(LumberjackFormatter_Tests, self).tearDown()

    # parse - two ways to specify included fields- fmt is list or in parens in string
    def test_parse_format_list(self):
        formatter = LumberjackFormatter(fmt=['a','b'], all_standard_fields=False)

        msg = json.loads(formatter.format(self.extras_rec))

        eq_(set(msg.keys()), set(('a','b','@timestamp','@source_host','@message')),
            msg='message should have only keys a, b, and required fields')

        eq_(msg['a'], 'sentinel.a', msg='sentinel value should be in a')
        eq_(msg['b'], 'sentinel.b', msg='sentinel value should be in b')

    def test_parse_format_string(self):
        formatter = LumberjackFormatter(fmt='%(a) blah blah %(b)', all_standard_fields=False, all_extra_fields=False)

        msg = json.loads(formatter.format(self.extras_rec))

        log.info(str(msg))

        eq_(set(msg.keys()), set(('a','b','@timestamp','@source_host','@message')),
            msg='message should have only keys a, b, and required fields')

        eq_(msg['a'], 'sentinel.a', msg='sentinel value should be in a')
        eq_(msg['b'], 'sentinel.b', msg='sentinel value should be in b')

    # format - message is formatted
    def test_format_no_extras(self):
        formatter = LumberjackFormatter(fmt=['@message'], all_standard_fields=False, all_extra_fields=False)

        msg = json.loads(formatter.format(self.extras_rec))

        log.info(str(msg))

        for k in msg.keys():
            assert_in(k, ('@timestamp', '@source_host', '@message'),
                      msg='message should only have timestamp and other required fields')

    # all_standard_fields - all and only fields which are present on the record are in the json format
    def test_format_all_standard_fields(self):
        formatter = LumberjackFormatter(fmt=self.STANDARD_LOG_ATTRS, all_standard_fields=True)

        msg = json.loads(formatter.format(self.blank_rec))

        # check all the standard attributes are present
        for k in self.STANDARD_LOG_ATTRS + ('@timestamp', '@source_host'):
            if k == 'message':
                k = '@%s' % k
            assert_in(k, msg, msg='standard attribute %s should be present' % k)

    # additional iso8601 field - present when configured, right format, timezone corresponds
    def test_iso8601_timestamp(self):
        formatter = LumberjackFormatter(fmt=['timestamp'], all_standard_fields=False)

        msg = json.loads(formatter.format(self.blank_rec))

        log.info(str(msg))

        assert_in('@timestamp', msg, msg='message should contain timestamp')

        for k in msg.keys():
            assert_in(k, ('@timestamp', '@source_host', '@message'),
                      msg='message should only have timestamp and other required fields')

        m = self.ISO8601_PATTERN.match(msg['@timestamp'])
        assert_is_not_none(m, msg='timestamp field should be in ISO8601 format')
        eq_(int(m.group(1)), 1970, msg='year should be 1970')
        eq_(int(m.group(2)), 1, msg='month should be 1')
        eq_(int(m.group(3)), 1, msg='day should be 1')
        eq_(int(m.group(4)), 0, msg='hour should be 0')
        eq_(int(m.group(5)), 0, msg='minute should be 0')
        eq_(float(m.group(7)), 1e-06, msg='second and microseconds should be 0.000001')
        assert_in(m.group(9), ('+00:00','Z'), msg='timezone should be UTC')

# vim: set ts=4 sw=4 expandtab:
