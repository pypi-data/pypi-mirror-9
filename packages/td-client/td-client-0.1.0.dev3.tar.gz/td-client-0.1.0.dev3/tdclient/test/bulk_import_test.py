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

def test_create_bulk_import_success():
    td = api.API("APIKEY")
    res = mock.MagicMock()
    res.status = 200
    td.post = mock.MagicMock(return_value=(res.status, b"", res))
    td.create_bulk_import("name", "db", "table")
    td.post.assert_called_with("/v3/bulk_import/create/name/db/table", {})

def test_delete_bulk_import_success():
    td = api.API("APIKEY")
    res = mock.MagicMock()
    res.status = 200
    td.post = mock.MagicMock(return_value=(res.status, b"", res))
    td.delete_bulk_import("name")
    td.post.assert_called_with("/v3/bulk_import/delete/name", {})

def test_show_bulk_import_success():
    td = api.API("APIKEY")
    # TODO: should be replaced by wire dump
    body = b"""
        {
            "status": "SUCCESS"
        }
    """
    res = mock.MagicMock()
    res.status = 200
    td.get = mock.MagicMock(return_value=(res.status, body, res))
    status = td.show_bulk_import("name")
    td.get.assert_called_with("/v3/bulk_import/show/name")
    assert status == "SUCCESS"

def test_list_bulk_imports_success():
    td = api.API("APIKEY")
    # TODO: should be replaced by wire dump
    body = b"""
        {
            "bulk_imports":[
            ]
        }
    """
    res = mock.MagicMock()
    res.status = 200
    td.get = mock.MagicMock(return_value=(res.status, body, res))
    bulk_imports = td.list_bulk_imports()
    td.get.assert_called_with("/v3/bulk_import/list", {})
    assert len(bulk_imports) == 0

def test_list_bulk_imports_failure():
    td = api.API("APIKEY")
    res = mock.MagicMock()
    res.status = 500
    td.get = mock.MagicMock(return_value=(res.status, b"error", res))
    with pytest.raises(api.APIError) as error:
        td.list_bulk_imports()
    assert error.value.args == ("500: List bulk imports failed: error",)

def test_list_bulk_import_parts_success():
    td = api.API("APIKEY")
    # TODO: should be replaced by wire dump
    body = b"""
        {
            "parts":[
            ]
        }
    """
    res = mock.MagicMock()
    res.status = 200
    td.get = mock.MagicMock(return_value=(res.status, body, res))
    parts = td.list_bulk_import_parts("foo")
    td.get.assert_called_with("/v3/bulk_import/list_parts/foo", {})
    assert len(parts) == 0

def test_list_bulk_import_upload_part_success():
    td = api.API("APIKEY")
    res = mock.MagicMock()
    res.status = 200
    td.put = mock.MagicMock(return_value=(res.status, b"", res))
    td.bulk_import_upload_part("name", "part_name", "stream", 1024)
    td.put.assert_called_with("/v3/bulk_import/upload_part/name/part_name", "stream", 1024)

def test_list_bulk_import_delete_part_success():
    td = api.API("APIKEY")
    res = mock.MagicMock()
    res.status = 200
    td.post = mock.MagicMock(return_value=(res.status, b"", res))
    td.bulk_import_delete_part("name", "part_name")
    td.post.assert_called_with("/v3/bulk_import/delete_part/name/part_name", {})

def test_freeze_bulk_import_success():
    td = api.API("APIKEY")
    res = mock.MagicMock()
    res.status = 200
    td.post = mock.MagicMock(return_value=(res.status, b"", res))
    td.freeze_bulk_import("name")
    td.post.assert_called_with("/v3/bulk_import/freeze/name", {})

def test_unfreeze_bulk_import_success():
    td = api.API("APIKEY")
    res = mock.MagicMock()
    res.status = 200
    td.post = mock.MagicMock(return_value=(res.status, b"", res))
    td.unfreeze_bulk_import("name")
    td.post.assert_called_with("/v3/bulk_import/unfreeze/name", {})

def test_perform_bulk_import_success():
    td = api.API("APIKEY")
    # TODO: should be replaced by wire dump
    body = b"""
        {
            "job_id": "12345"
        }
    """
    res = mock.MagicMock()
    res.status = 200
    td.post = mock.MagicMock(return_value=(res.status, body, res))
    job_id = td.perform_bulk_import("name")
    td.post.assert_called_with("/v3/bulk_import/perform/name", {})
    assert job_id == "12345"

def test_commit_bulk_import_success():
    td = api.API("APIKEY")
    # TODO: should be replaced by wire dump
    res = mock.MagicMock()
    res.status = 200
    td.post = mock.MagicMock(return_value=(res.status, b"", res))
    td.commit_bulk_import("name")
    td.post.assert_called_with("/v3/bulk_import/commit/name", {})

#def test_bulk_import_error_records_success():
#    td = api.API("APIKEY")
#    # TODO: should be replaced by wire dump
#    res = mock.MagicMock()
#    res.status = 200
#    td.post = mock.MagicMock(return_value=(res.status, b"", res))
#    td.bulk_import_error_records("name")
#    td.post.assert_called_with("/v3/bulk_import/error_records/name", {})
