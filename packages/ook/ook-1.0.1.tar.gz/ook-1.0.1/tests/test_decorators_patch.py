"""Tests for `ook.decorators.patch`."""

try:
    reload
except NameError:
    from imp import reload  # pylint: disable=redefined-builtin

from itertools import chain, combinations, product

from ook import patch
from ook.decorators import PY_VERSION
from ook.util import Version

import tests.examples

from tests import VERSION_ARGS


def powerset(seq):
    """powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"""
    # https://docs.python.org/3/library/itertools.html#itertools-recipes
    return chain.from_iterable(combinations(seq, r) for r in range(len(seq)+1))


def test_undecorated():
    """`tests.examples.basic()` returns 'undecorated'"""
    reload(tests.examples)
    assert tests.examples.basic() == "undecorated"


def test_version_args(args, kwargs):
    """`ook.patch` function respects version arguments"""
    reload(tests.examples)

    @patch(tests.examples, *args, **kwargs)
    def basic():
        """Return version arguments."""
        return args, kwargs

    ge_min = ("min" not in kwargs) or (PY_VERSION >= Version(kwargs["min"]))
    le_max = ("max" not in kwargs) or (PY_VERSION <= Version(kwargs["max"]))
    matches_specified = (not args) or (PY_VERSION in map(Version, args))
    if matches_specified and ge_min and le_max:
        assert tests.examples.basic == basic
        assert tests.examples.basic() == (args, kwargs)
    else:
        assert tests.examples.basic != basic
        assert tests.examples.basic() == "undecorated"


def pytest_generate_tests(metafunc):
    """Generate tests for `test_version_args`."""
    argnames = ["args", "kwargs"]
    if all(a in metafunc.funcargnames for a in argnames):
        argvalues = []
        for args in powerset(VERSION_ARGS):
            for keys in powerset(["min", "max"]):
                for values in product(VERSION_ARGS, repeat=len(keys)):
                    kwargs = dict(zip(keys, values))
                    argvalues.append((args, kwargs))
        metafunc.parametrize(argnames, argvalues)
