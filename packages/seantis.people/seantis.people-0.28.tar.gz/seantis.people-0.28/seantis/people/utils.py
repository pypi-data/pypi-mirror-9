from collections import MutableSequence
from uuid import UUID


class UUIDList(MutableSequence):
    """ A class that acts exactly like a list, but only accepts UUIDS. In case
    of another 'typed' class or acute bordedom implement as a metaclass.

    """

    def __init__(self, data=None):
        self._list = list()

        if data is not None:
            map(self.append, data)

    def get_uuid(self, item):
        if not isinstance(item, UUID):
            return UUID(item).hex
        else:
            return item.hex

    def __eq__(self, other):
        if not hasattr(other, '_list'):
            return False
        return self._list == other._list

    def __len__(self):
        return len(self._list)

    def __getitem__(self, i):
        return self._list[i]

    def __delitem__(self, i):
        del self._list[i]

    def __setitem__(self, i, item):
        self._list[i] = self.get_uuid(item)

    def __str__(self):
        return str(self._list)

    def __repr__(self):
        return 'UUIDList({})'.format(repr(self._list))

    def insert(self, i, item):
        self._list.insert(i, self.get_uuid(item))

    def append(self, item):
        self.insert(len(self._list), self.get_uuid(item))


class LinkList(list):
    """ A class containing a list of tuples containing title, url. Used
    to render a <ul><li><a href="url">title</a></li></ul> list.

    """
