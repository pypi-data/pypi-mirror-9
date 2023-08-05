from zope.interface import implements
from seantis.people.interfaces import IMembershipChangedEvent, IPersonMarker


class MembershipChangedEvent(object):
    implements(IMembershipChangedEvent)

    def __init__(self, person):
        assert IPersonMarker.providedBy(person)
        self.person = person
