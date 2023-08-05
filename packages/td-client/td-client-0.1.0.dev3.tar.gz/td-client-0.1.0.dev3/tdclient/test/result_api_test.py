#!/usr/bin/env python

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import with_statement

try:
    from unittest import mock
except ImportError:
    import mock
import pytest

from tdclient import api
from tdclient.test.test_helper import *

def setup_function(function):
    unset_environ()

def test_list_result_success():
    td = api.API("APIKEY")
    # TODO: should be replaced by wire dump
    body = b"""
        {
            "results":[
              {"name":"foo","url":"http://example.com/1"},
              {"name":"bar","url":"http://example.com/2"},
              {"name":"baz","url":"http://example.com/3"}
            ]
        }
    """
    res = mock.MagicMock()
    res.status = 200
    td.get = mock.MagicMock(return_value=(res.status, body, res))
    results = td.list_result()
    td.get.assert_called_with("/v3/result/list")
    assert len(results) == 3

def test_list_result_success():
    td = api.API("APIKEY")
    res = mock.MagicMock()
    res.status = 500
    td.get = mock.MagicMock(return_value=(res.status, b"error", res))
    with pytest.raises(api.APIError) as error:
        td.list_result()
    assert error.value.args == ("500: List result table failed: error",)

def test_create_result_success():
    td = api.API("APIKEY")
    res = mock.MagicMock()
    res.status = 200
    td.post = mock.MagicMock(return_value=(res.status, b"", res))
    results = td.create_result("foo", "http://example.com")
    td.post.assert_called_with("/v3/result/create/foo", {"url": "http://example.com"})

def test_delete_result_success():
    td = api.API("APIKEY")
    res = mock.MagicMock()
    res.status = 200
    td.post = mock.MagicMock(return_value=(res.status, b"", res))
    results = td.delete_result("foo")
    td.post.assert_called_with("/v3/result/delete/foo")
