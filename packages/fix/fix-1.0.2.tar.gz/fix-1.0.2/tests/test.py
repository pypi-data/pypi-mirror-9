"""Tests for `fix`."""

from types import ModuleType

import fix


def test_exists():
    """`fix` package exists"""
    assert isinstance(fix, ModuleType)
