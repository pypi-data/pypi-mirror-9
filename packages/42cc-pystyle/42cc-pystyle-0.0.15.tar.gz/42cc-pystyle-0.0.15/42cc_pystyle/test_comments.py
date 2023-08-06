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
                code = ast.parse(text[1:].lstrip())
                if len(code.body) == 1 and isinstance(code.body[0],
                                                      ast.Expr):
                    continue  # that's a simple one-word comment
                return start_index[1], '42cc4: Commented out code'
            except Exception:
                continue
