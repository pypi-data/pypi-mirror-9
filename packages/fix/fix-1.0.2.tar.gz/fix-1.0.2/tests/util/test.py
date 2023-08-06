"""Tests for `fix.util`."""

from types import ModuleType

import fix.util


def test_exists():
    """`fix.util` module exists"""
    assert isinstance(fix.util, ModuleType)
