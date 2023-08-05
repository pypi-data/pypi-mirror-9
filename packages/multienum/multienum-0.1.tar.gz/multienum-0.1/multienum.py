"""MultiEnum class for enumerations for multiple equivalent names.

Full documentation is in the README.  At present, this has only been tested in
CPython 3.4, although it should work for any recent version which allows
subclassing of the core int type.

"""

# pylint: disable=W0212

class MultiEnum(int):
    """Enumeration type as int sublcass with support for multiple names

    :cvar sequence _members: Sequence of members defining enumerated names
    :cvar sequence _fields: Names corresponding to the position within the
    member sequences

    :ivar str name: The default (first) name defined for the given value

    >>> class SampleEnum(MultiEnum):
    ...   _members = (("zero", "zip", "zero", "cero"),
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

    """
    _members = None
    _fields = None

    @classmethod
    def _resolve_value(cls, val):
        if type(val) is cls:
            # Already an enum
            return val
        if type(val) is int:
            intval = val
        else:
            try:
                intval = next(i for i in range(0, len(cls._members))
                              if str(val) in cls._members[i])
            except StopIteration:
                raise AttributeError(
                    "Enumeration name '%s' not in _members" % val)

        return intval

    def __new__(cls, *args, **kwargs):
        if cls._members is None:
            raise TypeError("No _members given at definition")

        retset = set()
        for val in args:
            retset.add(cls._resolve_value(val))

        for key, val in kwargs.items():
            findex = tuple(cls._fields).index(key)
            retset.add(tuple(m[findex] for m in cls._members).index(val))

        if len(retset) > 1:
            raise ValueError(
                "Init params to MultiEnum match different values")

        retval = next(iter(retset))
        if type(retval) is not cls:
            retval = super(MultiEnum, cls).__new__(cls, retval)
        retval._names = tuple(cls._members[int(retval)])
        return retval

    def __getattr__(self, key):
        if self._fields is None:
            raise AttributeError(
                "Attribute missing: MultiEnum object does not have _fields defined")

        try:
            index = next(i for i in range(0, len(self._fields))
                         if key == self._fields[i])
        except StopIteration:
            raise AttributeError("Enumeration name '%s' not defined" % key)

        return self._names[index]

    @property
    def name(self):
        """Default name for number"""
        return self._names[0]

    def __str__(self):
        return self._names[0]

    def __repr__(self):
        return "'%s'"  % self._names[0]
