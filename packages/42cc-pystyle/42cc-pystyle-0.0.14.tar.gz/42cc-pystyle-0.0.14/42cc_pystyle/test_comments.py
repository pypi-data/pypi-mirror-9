"""Function should not contain commented out code"""

import ast
import tokenize


def flake8ext(f):
    f.name = __name__
    f.version = '0.0.1'
    f.skip_on_py3 = False
    return f


@flake8ext
def commentedcode(physical_line, tokens):
    for token_type, text, start_index, _, _ in tokens:
        if token_type == tokenize.COMMENT:
            try:
                ast.parse(text[1:].lstrip())
                return start_index[1], '42cc4: Commented out code'
            except Exception:
                continue
