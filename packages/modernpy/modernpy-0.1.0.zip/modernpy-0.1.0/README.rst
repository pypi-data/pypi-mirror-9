Modernpy
=================

Extension methods for built-in type in Python.

Usage
--------

Integer
--------
(123).instance_of(int)
(123).to_s() == "123"
(123).to_f() == 123.0 and (123).to_f().instance_of(float)

float
--------
(123.45).instance_of(float)
(123.45).to_s() == "123.45"
(123.45).to_i() == 123

str
--------
"hello".instance_of(str)
"hello".length == 5
"123".to_i() == 123
"123.45".to_f() == 123.45
"hello".to_s() == "hello"

Unicode
--------
u"hello".instance_of(unicode)
u"hello".length == 5
u"123".to_i() == 123
u"123.45".to_f() == 123.45
u"hello".to_s() == u"hello"

list
--------
[1, 2, 3, 4].instance_of(list)
[1, 2, 3, 4].length == 4
[1, 2, 3, 4].sum() == 10

tuple
--------
(1, 2, 3, 4).instance_of(tuple)
(1, 2, 3, 4).length == 4
(1, 2, 3, 4).sum() == 10
