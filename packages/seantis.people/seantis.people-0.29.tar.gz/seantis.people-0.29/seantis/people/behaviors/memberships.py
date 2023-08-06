from five import grok

from zope.component import getAdapters
from zope.interface import Interface
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from plone import api
from plone.uuid.interfaces import IUUID
from plone.indexer.decorator import indexer

from seantis.plonetools import tools
from seantis.people.interfaces import IMembershipSource, IMembership


@indexer(IMembership)
def membership_person(membership, **kw):
    """ Stores the person on each membership object for faster lookups. """
    if hasattr(membership.person, 'to_object'):
        person = membership.person.to_object
    else:
        person = membership.person

    return IUUID(person)


def on_membership_changed(event, *args, **kwargs):
    """ Listens to IMembershipChanged events relaying them to the Catalog
    for reindexing of the person whose membership changed.

    """
    notify(ObjectModifiedEvent(event.person))


def on_membership_content_item_changed(context, event):
    if hasattr(context.person, 'to_object'):
        notify(ObjectModifiedEvent(context.person.to_object))
    else:
        notify(ObjectModifiedEvent(context.person))


def on_parent_folder_modified(context, event=None):
    """ Listens to IObjectModifiedEvent events of folders and triggers
    reindexing for containing memberships.

    """

    catalog = api.portal.get_tool('portal_catalog')
    memberships = catalog(
        object_provides=IMembership.__identifier__,
        path={'query': '/'.join(context.getPhysicalPath()), 'depth': 1}
    )

    for membership in memberships:
        notify(ObjectModifiedEvent(membership.getObject()))


def get_memberships(person=None, org_filter=None):
    context = api.portal.get()

    organizations = {}
    for name, source in getAdapters((context, ), IMembershipSource):
        for organization, memberships in source.memberships(person).items():

            if callable(org_filter):
                if not org_filter(organization, memberships):
                    continue

            if organization not in organizations:
                organizations[organization] = []

            organizations[organization].extend(memberships)

    return organizations


class ZodbMembershipSource(grok.Adapter):

    grok.name('zodb-membership-source')
    grok.provides(IMembershipSource)
    grok.context(Interface)

    def memberships(self, person=None):

        query = {
            'object_provides': IMembership.__identifier__,
            'sort_on': 'getObjPositionInParent'
        }

        if person is not None:
            query['membership_person'] = IUUID(person)

        # memberships are stored outside the people's list, so the normal
        # catalog is used instead of the people's catalog
        memberships = api.portal.get_tool('portal_catalog')(**query)

        result = {}

        for membership in (m.getObject() for m in memberships):
            organization = IUUID(tools.get_parent(membership))
            result.setdefault(organization, []).append(membership)

        return result
