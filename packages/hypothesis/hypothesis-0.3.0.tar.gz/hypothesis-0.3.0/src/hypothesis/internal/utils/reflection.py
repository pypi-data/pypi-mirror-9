"""
This file can approximately be considered the collection of hypothesis going to
really unreasonable lengths to produce pretty output.
"""

import inspect
from six.moves import xrange
import six
import types
import ast
import re


def convert_keyword_arguments(function, args, kwargs):
    """
    Returns a pair of a tuple and a dictionary which would be equivalent
    passed as positional and keyword args to the function. Unless function has
    **kwargs the dictionary will always be empty.
    """
    argspec = inspect.getargspec(function)
    new_args = []
    kwargs = dict(kwargs)

    defaults = {}

    if argspec.defaults:
        for name, value in zip(
            argspec.args[-len(argspec.defaults):], argspec.defaults
        ):
            defaults[name] = value

    n = max(len(args), len(argspec.args))

    for i in xrange(n):
        if i < len(args):
            new_args.append(args[i])
        else:
            arg_name = argspec.args[i]
            if arg_name in kwargs:
                new_args.append(kwargs.pop(arg_name))
            elif arg_name in defaults:
                new_args.append(defaults[arg_name])
            else:
                raise TypeError("No value provided for argument %r" % (
                    arg_name
                ))

    if kwargs and not argspec.keywords:
        if len(kwargs) > 1:
            raise TypeError("%s() got unexpected keyword arguments %s" % (
                function.__name__, ', '.join(map(repr, kwargs))
            ))
        else:
            bad_kwarg = next(iter(kwargs))
            raise TypeError("%s() got an unexpected keyword argument %r" % (
                function.__name__, bad_kwarg
            ))
    return tuple(new_args), kwargs


def extract_all_lambdas(tree):
    lambdas = []

    class Visitor(ast.NodeVisitor):
        def visit_Lambda(self, node):
            lambdas.append(node)

    Visitor().visit(tree)

    return lambdas


if six.PY3:  # pragma: no branch
    ARG_NAME_ATTRIBUTE = 'arg'  # pragma: no cover
else:
    ARG_NAME_ATTRIBUTE = 'id'   # pragma: no cover


def args_for_lambda_ast(l):
    return [getattr(n, ARG_NAME_ATTRIBUTE) for n in l.args.args]


def find_offset(string, line, column):
    current_line = 1
    current_line_offset = 0
    while current_line < line:
        current_line_offset = string.index("\n", current_line_offset+1)
        current_line += 1
    return current_line_offset + column


WHITESPACE = re.compile('\s+')
PROBABLY_A_COMMENT = re.compile("""#[^'"]*$""")


def extract_lambda_source(f):
    """
    Extracts a single lambda expression from the string source. Returns a
    string indicating an unknown body if it gets confused in any way.

    This is not a good function and I am sorry for it. Forgive me my sins, oh
    lord
    """
    args = inspect.getargspec(f).args
    if_confused = "lambda %s: <unknown>" % (', '.join(args),)
    try:
        source = inspect.getsource(f)
    except IOError:
        return if_confused

    try:
        try:
            tree = ast.parse(source)
        except IndentationError:
            source = "with 0:\n" + source
            tree = ast.parse(source)
    except SyntaxError:
        return if_confused

    all_lambdas = extract_all_lambdas(tree)
    aligned_lambdas = [
        l for l in all_lambdas
        if args_for_lambda_ast(l) == args
    ]
    if len(aligned_lambdas) != 1:
        return if_confused
    lambda_ast = aligned_lambdas[0]
    line_start = lambda_ast.lineno
    column_offset = lambda_ast.col_offset
    source = source[find_offset(source, line_start, column_offset):].strip()

    source = source[source.index("lambda"):]

    for i in xrange(len(source), -1, -1):  # pragma: no branch
        try:
            parsed = ast.parse(source[:i])
            assert len(parsed.body) == 1
            assert parsed.body
            if not isinstance(parsed.body[0].value, ast.Lambda):
                continue
            source = source[:i]
            break
        except SyntaxError:
            pass
    lines = source.split("\n")
    lines = [PROBABLY_A_COMMENT.sub("", l) for l in lines]
    source = '\n'.join(lines)

    source = WHITESPACE.sub(" ", source)
    source = source.strip()
    return source


def get_pretty_function_description(f):
    name = f.__name__
    if name == '<lambda>':
        return extract_lambda_source(f)
    elif isinstance(f, types.MethodType):
        self = f.__self__
        if not (self is None or inspect.isclass(self)):
            return "%r.%s" % (self, name)
    return name
