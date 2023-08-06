"""Function should not be too long"""

import ast


class TestLenFunction(object):
    name = 'test_lenfunction'
    version = '0.0.1'
    threshold = 40  # should have less than 40 statements in a function

    def __init__(self, tree, filename='(none)', builtins=None):
        self.tree = tree
        self.filename = filename

    def run(self):
        """Check that functions are less than threshold"""
        for stmt in ast.walk(self.tree):
            if isinstance(stmt, ast.FunctionDef) \
               and len(stmt.body) > self.threshold:
                yield (stmt.lineno, stmt.col_offset,
                       '42cc2: Function should be shorter than '
                       '%d statements' % self.threshold,
                       '42cc2',
                       )
