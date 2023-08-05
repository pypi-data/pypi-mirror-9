MultiEnum
=========

An enumeration type supporting multiple equivalent names.

Rationale
---------

I find the types defined in the built-in ``enum`` type in Python 3 to be
clumsy and hard to use for my purposes.  Further, I have a project which
repeatedly requires me to resolve strings to numbers and then back to
sometimes different strings, based on the context.  This module is the
result of that.

The implementation subclasses ``int``, which allows for the value of the
enumeration to be stored in a minimal amount of space, while providing a
number of attributes of the object for converting it to different names.

Usage
-----

Subclasses should define the class attribute ``_members`` as a tuple of
tuples. [#]_ Every member of ``_members`` should be a tuple of strings
containing a name which equates to the enumerated value.  The value will be
inferred from the member's position in the tuple (equal to the
subscript). Optionally, a subclass may define ``_fields``, a tuple of field
names which correspond to the order the enumeration names appear in within the
``_members`` attribute.

The enumerated value can be instantiated with a plain int value or with any of
the names provided in ``_members``, either using the appropriate field name as
a keyword or, so long as it is unique across all fields, as an un-keyworded
argument.  There is no test to ensure that names are unique -- if a name
appears multiple times in the ``_members`` tuples, the behavior is undefined.


By default, the first in each individual enumerated tuple will be returned if
the value is cast as a string (using the str() function, for instance).  For
compatability with the types in the ``enum`` module, the same value will be
returned using the ``name`` attribute.  The other names are available as a
tuple in the ``_names`` attribute, and if ``_fields`` was defined, will be
available as the value of attributes corresponding to the relevant field name
in ``_fields``.

If more than one argument is given on instantiation, either keyworded or not,
a ``ValueError`` exception will be raised unless all arguments resolve to the
same value.

The ``MultiEnum`` type makes an attempt to be idempotent -- i.e., if ``x`` is
an ``MultiEnum``, ``x is MultiEnum(x)`` should be true.  However, in the case
of multiple init values, idempotency is only preserved for the first
positional parameter.  ``x is MultiEnum(a, x)`` will not be true, even if
``a`` and ``x`` are equal.


.. [#] Techincally, the ``_members`` attribute, all members of ``_members``,
       and the ``_fields`` attribute can be any iterable sequence. I strongly
       recommend tuples unless you have a reason not to, because in addition
       to being lightweight and simple, they're immutable, which saves the
       interpreter a lot of work.

Example
-------

    >>> from multienum import MultiEnum
    >>> class SampleEnum(MultiEnum):
    ...   _members = (("zero", "zip", "zéro", "cero"),
    ...               ("one", "ace", "une", "uno"),
    ...               ("two", "deuce", "deux", "dos"))
    ...   _fields = ('english', 'slang', 'french', 'spanish')
    >>> val1 = SampleEnum("one")
    >>> int(val1)
    1
    >>> str(val1)
    'one'
    >>> val1.name
    'one'
    >>> val1.spanish
    'uno'
    >>> val2 = SampleEnum(slang="deuce")
    >>> int(val2)
    2
    >>> try:
    ...   se = SampleEnum("two", spanish="cero")
    ... except ValueError:
    ...   print("Value mismatch")
    Value mismatch



