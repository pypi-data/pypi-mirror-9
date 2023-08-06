#!/usr/bin/env python
# pylint:disable=R0201

"""Integration tests for the `yorm.settings.fake` option."""

import os
import pytest
from unittest.mock import patch

import yorm

from . import strip


@patch('yorm.settings.fake', True)
class TestFake:

    """Integration tests with `yorm.fake` enabled."""

    @yorm.attr(value=yorm.standard.Integer)
    @yorm.sync("path/to/{self.name}.yml")
    class Sample:

        """Sample class for fake mapping."""

        def __init__(self, name):
            self.name = name
            self.value = 0

    def test_fake(self, tmpdir):
        """Verify no file is created with fake enabled."""
        tmpdir.chdir()
        sample = self.Sample('sample')

        # ensure no file is created
        assert "path/to/sample.yml" == sample.yorm_path
        assert not os.path.exists(sample.yorm_path)

        # change object values
        sample.value = 42

        # check fake file
        assert strip("""
        value: 42
        """) == sample.yorm_fake

        # ensure no file is created
        assert not os.path.exists(sample.yorm_path)

        # change fake file
        text = strip("""
        value2: abc
        """)
        setattr(sample, 'yorm_fake', text)

        # check object values
        assert "abc" == sample.value2

        # ensure no file is created
        assert not os.path.exists(sample.yorm_path)


if __name__ == '__main__':
    pytest.main()
