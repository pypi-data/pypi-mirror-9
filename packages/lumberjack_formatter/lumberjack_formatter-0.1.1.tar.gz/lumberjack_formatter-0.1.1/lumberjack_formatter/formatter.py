try:
    from collections import OrderedDict
except ImportError:
    pass

import re
import math
import json
import time
import socket
import logging
import datetime
import collections

from .errors import FormatterInitializationException, IllegalInputException

from six import string_types




class LumberjackFormatter(logging.Formatter):
    # reserved attributes from http://docs.python.org/library/logging.html#logrecord-attributes
    # TODO programmatic way to glean these
    RESERVED_ATTRS = ('args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename', 'funcName', 'levelname',
                      'levelno', 'lineno', 'module', 'msecs', 'message', 'msg', 'name', 'pathname', 'process',
                      'processName', 'relativeCreated', 'thread', 'threadName')

    DEFAULT_ATTRS = ('exc_info', 'exc_text', 'filename', 'funcName', 'levelname', 'levelno', 'lineno', 'module',
                     'name', 'pathname', 'process', 'processName', 'relativeCreated', 'thread', 'threadName')

    RESERVED_ATTR_DICT = {k: None for k in RESERVED_ATTRS}

    STANDARD_FORMATTERS = re.compile(r'\((.+?)\)', re.IGNORECASE)

    def __init__(self, fmt=DEFAULT_ATTRS, *args, **kwargs):
        """
        :param args: standard formatter arguments fmt and datefmt
        :param kwargs:
            json_default - sets the handler for converting objects to something that can be serialized by json. note
                           that if you override this you will remove the default ISO8601 date formatting behavior.
            json_encoder - like the json_default, but implemented as a subclass of JSONEncoder.  this provides a means
                           to override not only the default, but encode and iterencode.
        """
        self.json_default = kwargs.pop('json_default', LumberjackFormatter.default_json_formatter)
        self.json_encoder = kwargs.pop('json_encoder', None)
        self.all_standard_fields = kwargs.pop('all_standard_fields', True)
        self.all_extra_fields = kwargs.pop('all_extra_fields', True)

        logging.Formatter.__init__(self, fmt, *args, **kwargs)

        self._configured_fields = self.parse_fmt()

        self._configured_fields = map(lambda f: '@%s' % f if f in ('timestamp', 'message', 'source_host') else f,
                                      self._configured_fields)

    def parse_fmt(self):
        if isinstance(self._fmt, string_types):
            return list(LumberjackFormatter.STANDARD_FORMATTERS.findall(self._fmt))
        elif isinstance(self._fmt, (collections.Sequence, collections.Set)):
            return list(self._fmt)
        else:
            raise FormatterInitializationException("unrecognized fmt type '%s'" % self._fmt.__class__)

    @classmethod
    def default_json_formatter(cls, obj):
        if isinstance(obj, datetime.datetime):
            return cls._date_formatter(obj)
        else:
            return str(obj)

    @staticmethod
    def _date_formatter(dt):
        assert isinstance(dt, datetime.datetime), 'expected datetime object'

        # assume naive instances are UTC, as generated in the formatter
        if dt.tzinfo is None:
            return dt.isoformat() + 'Z'
        else:
            return dt.isoformat()

    @classmethod
    def _validate_extras(cls, extras):
        for k in extras.keys():
            if k in cls.RESERVED_ATTR_DICT:
                raise IllegalInputException('cannot use reserved logrecord attribute ', key=k)

    def format(self, record):
        try:
            json_record = OrderedDict()
        except NameError:
            json_record = dict()

        # populate record fields
        record_fields = dict(record.__dict__)

        # save extra fields for later merging
        extras = record_fields.pop('extras', {})

        if not isinstance(extras, collections.Mapping):
            raise IllegalInputException('logrecord extras must be a mapping')

        self._validate_extras(extras)

        # merge select standard fields, or all of them
        field_whitelist_filter = lambda kvpair: kvpair[0] in self._configured_fields
        underscore_filter = lambda kvpair: not str(kvpair[0]).startswith('_')

        if self.all_standard_fields:
            json_record.update(record_fields)
        else:
            json_record.update(dict(filter(lambda x: field_whitelist_filter(x) and underscore_filter(x),
                                           record_fields.items())))

        # merge select extra fields, or all of them
        if self.all_extra_fields:
            json_record.update(extras)
        else:
            json_record.update(dict(filter(field_whitelist_filter, extras.items())))

        # insert fields that get populated by the formatter- asctime, message
        if 'asctime' in self._configured_fields:
            json_record['asctime']= self.formatTime(record, self.datefmt)

        # fields that are always present
        # NOTE utcfromtimestamp will retain microtime, but return a naive datetime instance
        json_record['@message'] = record.getMessage()
        json_record['@timestamp'] = datetime.datetime.utcfromtimestamp(record.created)
        json_record['@source_host'] = socket.gethostname()

        return json.dumps(json_record, default=self.json_default, cls=self.json_encoder)


# vim: set ts=4 sw=4 expandtab:
