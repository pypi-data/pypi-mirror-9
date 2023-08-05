"""

cicronus.util
~~~~~~~~~~~~~

Utility functions that other modules depend upon.

"""


from posixpath import sep as pathsep

from colour import Color


def get_check_id_from_cid(cid):
    """Get a check id integer from ``cid``.

    :param str cid: The check id.
    :rtype: :py:class:`int`

    """
    return int(cid.strip(pathsep).rpartition(pathsep)[-1])


def get_resource_from_cid(cid):
    """Get the resource name from ``cid``.

    :param str cid: The check id.
    :rtype: :py:class:`str`

    """
    return cid.strip(pathsep).split(pathsep)[0]


def colors(items):
    """Create a generator which returns colors for each item in ``items``.

    :param list items: The list to generate colors for.
    :rtype: generator(`colour.Color <https://pypi.python.org/pypi/colour>`_)

    """
    if len(items) < 2:
        c = (c for c in (Color("red"),))
    else:
        color_from = Color("red")
        color_to = Color("green")
        c = (color_from.range_to(color_to, len(items)))
    return c
