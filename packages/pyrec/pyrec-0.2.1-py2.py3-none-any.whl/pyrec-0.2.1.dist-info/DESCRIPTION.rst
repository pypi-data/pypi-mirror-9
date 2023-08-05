``Record`` is a datatype similar to the C ``struct``: an ordered collection of data members with predefined names. It's like the Python ``namedtuple`` but with mutable attributes and some extra conveniences.

::

    >>> from pyrec import Record

    >>> Point = Record('Point', 'x y z')

    >>> p = Point(1, 2, 3)
    >>> p.z = 9
    >>> p
    <Record object Point(x=1, y=2, z=9)>

For the full documentation, see https://github.com/bintoro/pyrec.


