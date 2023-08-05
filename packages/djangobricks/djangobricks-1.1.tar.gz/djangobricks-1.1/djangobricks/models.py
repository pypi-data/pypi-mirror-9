from __future__ import unicode_literals

import copy
from operator import attrgetter
from itertools import chain

from django.utils import six
from django.utils.six.moves import range

if six.PY3:
    def cmp(a, b):
        return (a > b) - (a < b)

SORTING_ASC = 1
SORTING_DESC = -1

# ---------------------------------------------------------------------------
# Criterion
# ---------------------------------------------------------------------------

class Criterion(object):
    """A criterion works as a sorting key for a :class:`BaseWall` subclass.

    It is a proxy to a value of a :class:BaseBrick subclass, whether it is a
    :class:`SingleBrick` or a :class:`ListBrick`.

    :param attrname: the name of the attribute to retrieve from an item of a
        :class:`SingleBrick`. Can be a callable that takes no argument.

    :param callback: a function that receives an item list and returns a
        single value for the ``attrname``, for example ``max``.

    :param default: the value to return when the item doesn't have the
         attribute, the ``callback``` is ``None`` or the item list is empty.
         Can be a callable that takes no argument.
    """

    def __init__(self, attrname, callback=None, default=None):
        self.attrname = attrname
        self.callback = callback
        self.default = default

    def __repr__(self):
        return self.attrname

    def get_value_for_item(self, item):
        """
        Returns a value for an item or the :attr:`default` if the item doesn't have
        any attribute :attr:`attrname`.
        """
        attrvalue = getattr(item, self.attrname, self.default)
        if callable(attrvalue):
            return attrvalue()
        return attrvalue

    def get_value_for_list(self, items=()):
        """
        Returns a single value for a list of items, filtering the values for
        each item through the :attr:`callback` function.
        If no :attr:`callback` is specified or if the item list is empty,
        it returns the :attr:`default` value.
        """
        if not isinstance(items, (list, tuple)):
            raise ValueError('List or tuple expected.')
        if items and self.callback is not None and callable(self.callback):
            # This is needed to avoid ValueError for some callback that can
            # not receive an empty list, like max()
            return self.callback([self.get_value_for_item(i) for i in items])
        return callable(self.default) and self.default() or self.default


# ---------------------------------------------------------------------------
# Brick
# ---------------------------------------------------------------------------

class BaseBrick(object):
    """Base class for a brick.

    A brick is a container for a single Django model instance or a list of
    instances. Subclasses should extend one of the two provided subclasses
    that implement those two use cases.
    """

    template_name = None #: The name of the template file to render the brick.

    def get_value_for_criterion(self, criterion):
        """Returns the criterion value for this brick."""
        raise NotImplementedError

    @classmethod
    def get_bricks_for_queryset(cls, queryset):
        """Returns a list of bricks from the given queryset."""
        raise NotImplementedError

    def get_context(self, **kwargs):
        """Returns the context to be passed on to the template."""
        return {}


class SingleBrick(BaseBrick):
    """Brick for a single object."""
    def __init__(self, item):
        self.item = item

    def __repr__(self):
        return repr(self.item)

    def get_value_for_criterion(self, criterion):
        return criterion.get_value_for_item(self.item)

    @classmethod
    def get_bricks_for_queryset(cls, queryset):
        """
        Returns an iterator over the bricks, one for each object in the
        queryset.
        """
        return (cls(i) for i in queryset)

    def get_context(self, **kwargs):
        """
        Returns the context to be passed on to the template.
        By default, it returns a dictionary instance with an *object* key
        and the item as the value.
        Subclass should first call the super method and then update the result.
        """
        return {'object': self.item}


class ListBrick(BaseBrick):
    """Brick for a list of objects."""
    chunk_size = 5 #: The default length of a list.

    def __init__(self, items):
        self.items = items

    def __repr__(self):
        return repr(self.items)

    def get_value_for_criterion(self, criterion):
        return criterion.get_value_for_list(self.items)

    @classmethod
    def get_bricks_for_queryset(cls, queryset):
        """
        Returns a list of bricks, each one containing :attr:`chunk_size`
        elements.
        """
        count = queryset.count()
        # Execute the query once to avoid several OFFSET LIMIT
        items = list(queryset)
        return [cls(i) for i in (items[i:i+cls.chunk_size]
                                 for i in range(0, count, cls.chunk_size))]

    def get_context(self, **kwargs):
        """
        Returns the context to be passed on to the template.
        By default, it returns a dictionary instance with an *object_list*
        key and the items as the value.
        Subclass should first call the super method and then update the result.
        """
        return {'object_list': self.items}


# ---------------------------------------------------------------------------
# Brick Manager
# ---------------------------------------------------------------------------

class BaseWall(object):
    """Manager for a list of bricks.

    It orders a list of bricks using the given criteria and can be sliced or
    iterated.

    :param bricks: the list of bricks to sort.
    :param criteria: the list of criteria to sort the bricks by.
    """

    def __init__(self, bricks, criteria=None):
        self.bricks = bricks
        self.criteria = criteria or []
        self._sorted = []

    def __getitem__(self, key):
        return self.sorted[key]

    def __iter__(self):
        return iter(self.sorted)

    def __len__(self):
        return len(self.bricks)

    def __getstate__(self):
        # We save the sorted bricks and delete che criteria
        # as those might not be pickable
        obj_dict = self.__dict__.copy()
        obj_dict['_sorted'] = self.sorted
        if 'criteria' in obj_dict:
            del obj_dict['criteria']
        return obj_dict

    def _cmp(self, left, right):
        """
        # Courtesy of:
        # http://stackoverflow.com/questions/1143671/python-sorting-list-of-dictionaries-by-multiple-keys
        """
        fn = attrgetter('get_value_for_criterion')
        for criterion, sorting_order in self.criteria:
            result = cmp(fn(left)(criterion), fn(right)(criterion))
            if result:
                return sorting_order * result
        else:
            return 0

    @property
    def sorted(self):
        """
        Lazy property that returns the list of bricks sorted by the criteria.
        """
        if not self._sorted:
            try:
                # Python > 2.6
                from functools import cmp_to_key
                self._sorted = sorted(self.bricks, key=cmp_to_key(self._cmp))
            except ImportError:
                # Python <= 2.6
                self._sorted = sorted(self.bricks, cmp=self._cmp)
        return self._sorted

    def filter(self, callback, operator='AND'):
        """
        Returns a copy of the wall where the bricks have been filtered using
        the given :attr:`callback`, that should be a function or a list of
        functions accepting a brick instance and returning a boolean.

        By default, if more than a callback is given they are *ANDed*, that is,
        a brick will pass the test if every callback returns ``True``.

        This behaviour can be changed by setting the :attr:`operator` parameter
        to ``OR``, in which case as soon as callback returns ``True`` the brick
        is accepted.
        """
        assert operator in ('OR', 'AND'), "Only 'AND' or 'OR' operators are supported"
        if not isinstance(callback, (list, tuple)):
            callback = [callback]
        # The order of bricks is the same even when filtered.
        # So we let the class to sort them (if they are not already) and then
        # apply the filter.
        obj = copy.copy(self)
        func = all if operator == 'AND' else any
        obj._sorted = [i for i in self if func(c(i) for c in callback)]
        # This will keep __len__ value consistent
        obj.bricks = obj._sorted
        return obj


# ---------------------------------------------------------------------------
# Wall Factory
# ---------------------------------------------------------------------------

class BaseWallFactory(object):
    """Helper class that simplifies and encapsulates the creation of a wall.

    :param criteria: the list of criteria to sort the bricks by.
    :param wall_class: an optional class for the wall.
        Must subclass :class:`BaseWall`
    """
    def __init__(self, criteria=None, wall_class=BaseWall):
        self.criteria = criteria or []
        self.wall_class = wall_class

    def get_content(self):
        """Must returns a list of tuples of two elements each.

        The first one is a Brick class and the second the queryset of objects
        that should be rendered using that class.

        E.g.:

        .. code-block:: python

            returns [
                (ArticleBrick, articles),
                (VideoBrick, videos),
                (NewsBrick, news),
            ]
        """
        raise NotImplementedError

    def wall(self):
        """Returns a configured instance of the wall.

        Normally you should not override this method unless you want to
        manipulate the list of bricks somehow. In that case make sure you call
        super before applying your logic.
        """
        def content_iterator():
            # Do some sanity check just to help the user
            for brick, queryset in self.get_content():
                if not issubclass(brick, BaseBrick):
                    raise TypeError("Expected a BaseBrick subclass, "
                                    "got %r instead" % brick)
                yield brick, queryset

        bricks = (b.get_bricks_for_queryset(qs) for b, qs in content_iterator())
        bricks_list = list(chain.from_iterable(bricks))
        return self.wall_class(bricks_list, self.criteria)

def wall_factory(content, brick_class, criteria=None, wall_class=BaseWall):
    """
    An utility method to configure a simple wall object that uses a single
    brick class.
    You can just pass the content as a queryset or a list of querysets, a custom
    brick class and a list of criteria.

    See the docs for sample usage.
    """
    # Cannot do that in the local scope of get_content!
    if not isinstance(content, (list, tuple)):
        content = [content]
    def get_content():
        return ((brick_class, queryset) for queryset in content)
    factory = BaseWallFactory(criteria, wall_class)
    # Monkey patch the factory instance
    factory.get_content = get_content
    return factory.wall()
