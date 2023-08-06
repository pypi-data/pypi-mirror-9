import modernpylib

# Test int
assert (123).instance_of(int)
assert (123).to_s() == "123"
assert (123).to_f() == 123.0 and (123).to_f().instance_of(float)

# Test float
assert (123.45).instance_of(float)
assert (123.45).to_s() == "123.45"
assert (123.45).to_i() == 123

# Test str
assert "hello".instance_of(str)
assert "hello".length == 5
assert "123".to_i() == 123
assert "123.45".to_f() == 123.45
assert "hello".to_s() == "hello"

# Test str
assert u"hello".instance_of(unicode)
assert u"hello".length == 5
assert u"123".to_i() == 123
assert u"123.45".to_f() == 123.45
assert u"hello".to_s() == u"hello"

# Test list
assert [1, 2, 3, 4].instance_of(list)
assert [1, 2, 3, 4].length == 4
assert [1, 2, 3, 4].sum() == 10

# Test tuple
assert (1, 2, 3, 4).instance_of(tuple)
assert (1, 2, 3, 4).length == 4
assert (1, 2, 3, 4).sum() == 10
