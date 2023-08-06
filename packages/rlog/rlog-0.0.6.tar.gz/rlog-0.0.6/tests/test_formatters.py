# coding: utf-8
import logging
import sys

from rlog._compat import json, PY3, PYPY
from rlog.formatters import JSONFormatter


def get_result_record(**kwargs):
    record = logging.makeLogRecord(kwargs)
    formatter = JSONFormatter()
    formatted_record = formatter.format(record)
    return json.loads(formatted_record)


def test_formatter():
    data = get_result_record(msg='Test %s', args=('format', ))
    assert data['msg'] == 'Test format'


def test_exception_info():
    try:
        1 / 0
    except ZeroDivisionError:
        data = get_result_record(exc_info=sys.exc_info())
        if PY3:
            error_string = 'ZeroDivisionError: division by zero'
        elif PYPY:
            error_string = 'ZeroDivisionError: integer division by zero'
        else:
            error_string = 'ZeroDivisionError: integer division or modulo by zero'
        assert error_string in data['exc_info']
