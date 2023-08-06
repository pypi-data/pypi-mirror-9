import ast
import sys

sys.path.append('..')

import test_docstrings

T = test_docstrings.TestDocstrings


def test_regular_function():
    "Regular function wo docstring should not fail"
    assert list(T(ast.parse('def func(): pass')).run()) == []


def test_test_with_docstring():
    "Test method with docstring should not fail"
    assert list(T(ast.parse('def test_func(): "docstring"')).run()) == []


def test_test_wo_docstring():
    "Test method without docstring should fail with `42cc1` code"
    assert list(T(ast.parse('def test_func(): pass')).run()) == [
        (1, 0, '42cc1: Test has no docstring', '42cc1')]
