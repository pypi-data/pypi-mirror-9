 # coding=utf-8
from nose.tools import assert_raises
from typechecks import is_string, require_string

def test_is_string():
    assert is_string("hello")
    assert is_string("")
    assert is_string(u"Ѽ")
    assert is_string(u"ﮚ")
    assert not is_string(1)
    assert not is_string(1.0)
    assert not is_string([])
    assert not is_string(object())
    assert not is_string(None)

def test_require_string():
    require_string("", nonempty=False)
    with assert_raises(TypeError):
        require_string(0, nonempty=False)
    with assert_raises(TypeError):
        require_string(0, nonempty=True)
    with assert_raises(ValueError):
        require_string("", nonempty=True)
    require_string("1", nonempty=False)
    require_string("1", nonempty=True)
