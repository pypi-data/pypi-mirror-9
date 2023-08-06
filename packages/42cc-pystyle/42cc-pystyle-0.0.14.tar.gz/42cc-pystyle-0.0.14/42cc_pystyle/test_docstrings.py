"""Tests should have docstrings"""

import ast


class TestDocstrings(object):
    name = 'test_docstrings'
    version = '0.0.1'

    def __init__(self, tree, filename='(none)', builtins=None):
        self.tree = tree
        self.filename = filename

    def run(self):
        """Check that test methods of test classes have docstrings"""
        for stmt in ast.walk(self.tree):
            if isinstance(stmt, ast.FunctionDef) \
               and stmt.name.startswith('test') \
               and not ast.get_docstring(stmt):
                yield (
                    stmt.lineno,
                    stmt.col_offset,
                    "42cc1: Test has no docstring",
                    "42cc1",
                )
