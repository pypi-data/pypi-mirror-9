#!/usr/bin/env python
# pylint:disable=W0201,W0613,R0201,W0212,C0111

"""Unit tests for the `base` module."""

import pytest
import logging
from unittest.mock import Mock

from yorm.base.mappable import get_mapper, Mappable
from yorm.base.convertible import Convertible
from yorm.mapper import Mapper
from yorm.converters import String, Integer, Boolean

from . import strip


class MockMapper(Mapper):

    """Mapped file with stubbed file IO."""

    def __init__(self, obj, path, attrs):
        super().__init__(obj, path, attrs)
        self._mock_file = None
        self._mock_modified = True
        self.exists = True

    def _read(self):
        text = self._mock_file
        logging.debug("mock read:\n%s", text.strip())
        return text

    def _write(self, text):
        logging.debug("mock write:\n%s", text.strip())
        self._mock_file = text
        self.modified = True

    @property
    def modified(self):
        return self._mock_modified

    @modified.setter
    def modified(self, changes):  # pylint: disable=W0221
        self._mock_modified = changes


# sample classes ###############################################################


class SampleMappable(Mappable):

    """Sample mappable class with hard-coded settings."""

    def __init__(self):
        self.yorm_mapper = None

        logging.debug("initializing sample...")
        self.var1 = None
        self.var2 = None
        self.var3 = None
        logging.debug("sample initialized")

        path = "mock/path/to/sample.yml"
        attrs = {'var1': String,
                 'var2': Integer,
                 'var3': Boolean}
        self.yorm_mapper = MockMapper(self, path, attrs)
        self.yorm_mapper.store()

    def __repr__(self):
        return "<sample {}>".format(id(self))


# tests ########################################################################


class TestGetMapper:

    """Unit tests for the `get_mapper` function."""

    def test_mappable_required(self):
        with pytest.raises(TypeError):
            print(get_mapper(None))

    def test_yorm_mapper_required(self):
        sample = SampleMappable()
        del sample.yorm_mapper
        with pytest.raises(AttributeError):
            print(get_mapper(sample))


class TestMappable:

    """Unit tests for the `Mappable` class."""

    def setup_method(self, method):
        """Create an mappable instance for tests."""
        self.sample = SampleMappable()

    def test_init(self):
        """Verify files are created after initialized."""
        text = self.sample.yorm_mapper._read()
        assert strip("""
        var1: ''
        var2: 0
        var3: false
        """) == text

    def test_set(self):
        """Verify the file is written to after setting an attribute."""
        self.sample.var1 = "abc123"
        self.sample.var2 = 1
        self.sample.var3 = True
        text = self.sample.yorm_mapper._read()
        assert strip("""
        var1: abc123
        var2: 1
        var3: true
        """) == text

    def test_set_converted(self):
        """Verify conversion occurs when setting attributes."""
        self.sample.var1 = 42
        self.sample.var2 = "1"
        self.sample.var3 = 'off'
        text = self.sample.yorm_mapper._read()
        assert strip("""
        var1: '42'
        var2: 1
        var3: false
        """) == text

    def test_set_error(self):
        """Verify an exception is raised when a value cannot be converted."""
        with pytest.raises(ValueError):
            self.sample.var2 = "abc"

    def test_get(self):
        """Verify the file is read from before getting an attribute."""
        text = strip("""
        var1: def456
        var2: 42
        var3: off
        """)
        self.sample.yorm_mapper._write(text)
        assert"def456" == self.sample.var1
        assert 42 == self.sample.var2
        assert False is self.sample.var3

    def test_error_invalid_yaml(self):
        """Verify an exception is raised on invalid YAML."""
        text = strip("""
        invalid: -
        """)
        self.sample.yorm_mapper._write(text)
        with pytest.raises(ValueError):
            print(self.sample.var1)

    def test_error_unexpected_yaml(self):
        """Verify an exception is raised on unexpected YAML."""
        text = strip("""
        not a dictionary
        """)
        self.sample.yorm_mapper._write(text)
        with pytest.raises(ValueError):
            print(self.sample.var1)

    def test_new(self):
        """Verify new attributes are added to the object."""
        text = strip("""
        new: 42
        """)
        self.sample.yorm_mapper._write(text)
        assert 42 == self.sample.new

    def test_new_unknown(self):
        """Verify an exception is raised on new attributes w/ unknown types"""
        text = strip("""
        new: !!timestamp 2001-12-15T02:59:43.1Z
        """)
        self.sample.yorm_mapper._write(text)
        with pytest.raises(ValueError):
            print(self.sample.var1)


class TestMappableTriggers:

    class MockList:

        def append(self, value):
            print(value)

    class MockDict(Mappable, dict):

        pass

    class Sample(MockList, MockDict):

        yorm_mapper = Mock()
        yorm_mapper.attrs = []
        yorm_mapper.fetch = Mock()
        yorm_mapper.store = Mock()

    def setup_method(self, method):
        """Create an mappable instance for tests."""
        self.sample = self.Sample()
        self.sample.yorm_mapper.fetch.reset_mock()
        self.sample.yorm_mapper.store.reset_mock()

    def test_getattribute(self):
        with pytest.raises(AttributeError):
            getattr(self.sample, 'foo')
        assert 1 == self.sample.yorm_mapper.fetch.call_count
        assert 0 == self.sample.yorm_mapper.store.call_count

    def test_setattr(self):
        self.sample.yorm_mapper.attrs.append('foo')
        setattr(self.sample, 'foo', 'bar')
        assert 0 == self.sample.yorm_mapper.fetch.call_count
        assert 1 == self.sample.yorm_mapper.store.call_count

    def test_getitem(self):
        with pytest.raises(KeyError):
            print(self.sample['foo'])
        assert 1 == self.sample.yorm_mapper.fetch.call_count
        assert 0 == self.sample.yorm_mapper.store.call_count

    def test_setitem(self):
        self.sample['foo'] = 'bar'
        assert 0 == self.sample.yorm_mapper.fetch.call_count
        assert 1 == self.sample.yorm_mapper.store.call_count

    def test_delitem(self):
        self.sample['foo'] = 'bar'
        self.sample.yorm_mapper.store.reset_mock()
        del self.sample['foo']
        assert 0 == self.sample.yorm_mapper.fetch.call_count
        assert 1 == self.sample.yorm_mapper.store.call_count

    def test_append(self):
        self.sample.append('foo')
        assert 0 == self.sample.yorm_mapper.fetch.call_count
        # assert 1 == self.sample.yorm_mapper.store.call_count

    def test_store_and_fetch_can_handle_missing_mapper(self):
        sample = self.MockDict()
        sample.yorm_mapper = None
        sample[0] = 0
        print(sample[0])
        assert None is sample.yorm_mapper


class TestConverter:

    """Unit tests for the `Convertible` class."""

    def test_not_implemented(self):
        """Verify `Convertible` cannot be used directly."""
        with pytest.raises(NotImplementedError):
            Convertible.to_value(None)  # pylint: disable=E1120
        with pytest.raises(NotImplementedError):
            Convertible.to_data(None)  # pylint: disable=E1120


if __name__ == '__main__':
    pytest.main()
