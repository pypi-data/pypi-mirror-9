def group_by_attr(attr, items, getattr_fn=getattr):
    """
    Group a sequence of items by a shared attribute.

    For example, let's say you have an object "Struct":
    >>> from pprint import pprint
    >>> from collections import namedtuple
    >>> Struct = namedtuple('Struct', ('x', 'y', 'z'))

    And you have a few Struct instances:
    >>> a, b, c = (
    ...     Struct(x=1, y=1, z=1),
    ...     Struct(x=1, y=2, z=2),
    ...     Struct(x=1, y=1, z=3))

    If we were to group these instances by the 'x' attribute, we should
    expect a single group containing all three items:
    >>> pprint(group_by_attr(attr='x', items=(a, b, c)))
    {1: (Struct(x=1, y=1, z=1),
         Struct(x=1, y=2, z=2),
         Struct(x=1, y=1, z=3))}

    If, instead, we were to group by 'y', we should expect a different
    grouping:
    >>> pprint(group_by_attr(attr='y', items=(a, b, c)))
    {1: (Struct(x=1, y=1, z=1),
         Struct(x=1, y=1, z=3)),
     2: (Struct(x=1, y=2, z=2),)}

    Finally, grouping by 'z' will result in three separate groups:
    >>> pprint(group_by_attr(attr='z', items=(a, b, c)))
    {1: (Struct(x=1, y=1, z=1),),
     2: (Struct(x=1, y=2, z=2),),
     3: (Struct(x=1, y=1, z=3),)}

    This function can also use an alternate getattr, as long as it implements
    the same interface (taking an item and an attribute name as arguments).
    For example, you could group dictionaries:
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
    """
    grouped = {}

    for i in items:
        v = getattr_fn(i, attr)
        grouped[v] = grouped.get(v, ()) + (i,)

    return grouped
