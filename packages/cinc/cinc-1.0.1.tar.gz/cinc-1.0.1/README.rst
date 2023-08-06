cinc provides fixed-width C-like integer types. These types are designed to be
as fast as Python's built-in int type.

=====
Usage
=====

Signed types are named "intN" and unsigned types are named "uintN", where "N"
is the number of bits. Types for 8, 16, 32 and 64 bits are provided.

cinc integers can be constructed from Python ints or cast from another cinc
type.

::

    >>> x = uint32(0xFFFFFFFF)
    >>> uint16(x)
    cinc.uint16(65535)

==========
Arithmetic
==========

cinc integers support all arithmetic operators. All cinc integers are
immutable, so operators return new objects.

There is no need to explicitly cast different types when using them together.
Every cinc type is compatible with every other cinc type::

    >>> x = uint32(2)
    >>> y = int32(2)
    >>> x + y
    cinc.uint32(4)
    >>> y + x
    cinc.int32(4)

The object returned by operators has the same type as the left operand.

cinc integers also have methods for bit rotate operations as well as bit
extraction and insertion.

Most operators and methods expect cinc objects for their arguments, but some
accept Python ints because it is common to use them with literals:

- The ``<<`` and ``>>`` operators.
- The ``lrotate`` and ``rrotate`` methods.
- The ``extract`` and ``insert`` methods.
