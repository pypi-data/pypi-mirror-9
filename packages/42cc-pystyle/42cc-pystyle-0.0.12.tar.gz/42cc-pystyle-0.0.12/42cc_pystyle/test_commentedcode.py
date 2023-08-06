"""Function should not contain commented out code"""

import ast


class TestCommentedCode(object):
    name = 'test_commentedcodef'
    version = '0.0.1'

    def __init__(self, tree, filename='(none)', builtins=None):
        self.tree = tree
        self.filename = filename

    def run(self):
        """Check that no functions contain commented code"""
        for stmt in ast.walk(self.tree):
            if isinstance(stmt, ast.FunctionDef):
                print stmt.body
                yield (stmt.lineno, stmt.col_offset,
                       '42cc4: Function contains commented out code',
                       '42cc4',
                       )
