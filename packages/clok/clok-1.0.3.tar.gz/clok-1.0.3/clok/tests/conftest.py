# conftest.py

import pytest

import mock as mockmodule
from tinydb import TinyDB
from tinydb.storages import MemoryStorage

from ..models import setup_db


@pytest.yield_fixture(scope="session")
def mock():
    yield mockmodule


@pytest.yield_fixture(scope="session")
def assert_raises():
    yield pytest.raises


@pytest.yield_fixture()
def test_db():
    yield TinyDB(storage=MemoryStorage)
    setup_db(None)  # "restore" missing DB after the test
