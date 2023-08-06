"""Function should not consist of a single `if` statement"""

import ast


class TestSingleIf(object):
    name = 'test_singleif'
    version = '0.0.1'

    def __init__(self, tree, filename='(none)', builtins=None):
        self.tree = tree
        self.filename = filename

    def run(self):
        """Check that no functions are a single if statement"""
        for stmt in ast.walk(self.tree):
            if isinstance(stmt, ast.FunctionDef):
                if len(stmt.body) > 1:
                    continue
                if isinstance(stmt.body[0], ast.If):
                    yield (stmt.lineno, stmt.col_offset,
                           '42cc3: Function should be longer than a '
                           'single if',
                           '42cc3',
                           )
