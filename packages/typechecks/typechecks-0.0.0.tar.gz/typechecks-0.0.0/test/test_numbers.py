 # coding=utf-8
from nose.tools import assert_raises
from typechecks import is_integer, require_integer

def test_is_integer():
    assert is_integer(0)
    assert is_integer(-1)
    assert is_integer(1)
    # big integer
    assert is_integer(10**30)
    assert not is_integer("")
    assert not is_integer("a")
    assert not is_integer([])
    assert not is_integer([1])
    assert not is_integer(object())
    assert not is_integer(None)

def test_require_integer():
    require_integer(0)
    require_integer(10)
    require_integer(-10)
    with assert_raises(TypeError):
        require_integer("")
    with assert_raises(TypeError):
        require_integer(None)