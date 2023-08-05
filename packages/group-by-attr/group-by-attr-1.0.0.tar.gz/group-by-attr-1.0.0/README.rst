group-by-attr |Version| |Build| |Coverage| |Health|
===================================================================

|Compatibility| |Implementations| |Format| |Downloads|

Group items in a sequence by the value of a shared attribute.

.. code:: python

    group_by_attr(attr, items)


Installation:

.. code:: shell

    $ pip install group-by-attr


Example
-------

Let's say you want to group some "Struct" instances together.

.. code:: python

    >>> from pprint import pprint
    >>> from collections import namedtuple
    >>> Struct = namedtuple('Struct', ('x', 'y', 'z'))
    >>> a, b, c = (
    ...     Struct(x=1, y=1, z=1),
    ...     Struct(x=1, y=2, z=2),
    ...     Struct(x=1, y=1, z=3))

If we were to group these instances by the 'x' attribute, we should
expect a single group containing all three items:

.. code:: python

    >>> pprint(group_by_attr(attr='x', items=(a, b, c)))
    {1: (Struct(x=1, y=1, z=1),
         Struct(x=1, y=2, z=2),
         Struct(x=1, y=1, z=3))}

If, instead, we were to group by 'y', we should expect a different
grouping:

.. code:: python

    >>> pprint(group_by_attr(attr='y', items=(a, b, c)))
    {1: (Struct(x=1, y=1, z=1),
         Struct(x=1, y=1, z=3)),
     2: (Struct(x=1, y=2, z=2),)}

Finally, grouping by 'z' will result in three separate groups:

.. code:: python

    >>> pprint(group_by_attr(attr='z', items=(a, b, c)))
    {1: (Struct(x=1, y=1, z=1),),
     2: (Struct(x=1, y=2, z=2),),
     3: (Struct(x=1, y=1, z=3),)}

This function can also use an alternate getattr, as long as it implements
the same interface (taking an item and an attribute name as arguments).
For example, you could group dictionaries:

.. code:: python

    >>> pprint(group_by_attr(
    ...     attr='x',
    ...     items=(
    ...         {'x': 1, 'y': 'a'},
    ...         {'x': 2, 'y': 'b'},
    ...         {'x': 1, 'y': 'c'}),
    ...     getattr_fn=dict.__getitem__))
    {1: ({'x': 1, 'y': 'a'},
         {'x': 1, 'y': 'c'}),
     2: ({'x': 2, 'y': 'b'},)}


.. |Build| image:: https://travis-ci.org/themattrix/python-group-by-attr.svg?branch=master
   :target: https://travis-ci.org/themattrix/python-group-by-attr
.. |Coverage| image:: https://img.shields.io/coveralls/themattrix/python-group-by-attr.svg
   :target: https://coveralls.io/r/themattrix/python-group-by-attr
.. |Health| image:: https://landscape.io/github/themattrix/python-group-by-attr/master/landscape.svg
   :target: https://landscape.io/github/themattrix/python-group-by-attr/master
.. |Version| image:: https://pypip.in/version/group-by-attr/badge.svg?text=version
    :target: https://pypi.python.org/pypi/group-by-attr
.. |Downloads| image:: https://pypip.in/download/group-by-attr/badge.svg
    :target: https://pypi.python.org/pypi/group-by-attr
.. |Compatibility| image:: https://pypip.in/py_versions/group-by-attr/badge.svg
    :target: https://pypi.python.org/pypi/group-by-attr
.. |Implementations| image:: https://pypip.in/implementation/group-by-attr/badge.svg
    :target: https://pypi.python.org/pypi/group-by-attr
.. |Format| image:: https://pypip.in/format/group-by-attr/badge.svg
    :target: https://pypi.python.org/pypi/group-by-attr
