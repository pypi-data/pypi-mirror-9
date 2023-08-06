from plone import api
from zope.interface import implements

from seantis.plonetools import tools
from seantis.people.interfaces import IPerson
from seantis.people.behaviors.memberships import get_memberships
from seantis.people.utils import UUIDList


class Person(object):
    implements(IPerson)

    def __init__(self, context):
        self.context = context

    def memberships(self, org_filter=None):
        return get_memberships(person=self.context, org_filter=org_filter)

    def organizations(self, org_filter=None):
        """ Returns a list of organizations this person is active in. The list
        is sorted by uca collation. This is mainly used for the organizations
        metadata field of all person objects (to show in the list).

        """

        organizations = self.organization_uuids(org_filter)

        # organizations are defined in the general catalog, not the people
        # catalog, which only contains people, therefore use 'portal_catalog'
        titles = []
        catalog = api.portal.get_tool('portal_catalog')
        for uid in organizations:
            title = catalog(UID=uid)[0].Title
            if isinstance(title, str):
                title = title.decode('utf-8')
            titles.append(title)

        return sorted(titles, key=tools.unicode_collate_sortkey())

    def organization_uuids(self, org_filter=None):
        """ Returns the organizations as uuid references which are be rendered
        as links in the list view.

        """
        organizations = UUIDList()

        for uuid, memberships in self.memberships().items():
            if callable(org_filter) and not org_filter(uuid, memberships):
                continue

            organizations.append(uuid)

        return organizations

    def current_role(self, memberships):
        """ Goes through the given memberships and returns the current role.
        The current role is the role of the first membership in the list.

        """

        if memberships:
            return memberships[0].role
        else:
            return u''
