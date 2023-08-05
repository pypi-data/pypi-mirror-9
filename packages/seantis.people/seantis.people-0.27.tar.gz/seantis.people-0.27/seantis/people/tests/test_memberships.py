from contextlib import contextmanager

from zope.component import getGlobalSiteManager, getAdapters
from zope.interface import Interface
from zope.event import notify

from plone import api
from plone.uuid.interfaces import IUUID

from seantis.plonetools import tools

from seantis.people import catalog_id
from seantis.people import tests
from seantis.people.events import MembershipChangedEvent
from seantis.people.interfaces import IMembershipSource, IPerson

from seantis.people.utils import UUIDList


class TestAdapter(object):

    def __init__(self, context):
        self.context = context


class Membership(object):

    def __init__(self, person, role=None):
        self.person = person
        self.role = role


class TestMemberships(tests.IntegrationTestCase):

    def register_membership_source(self, adapter, interface, name):
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(
            factory=adapter, required=(interface,), name=name,
            provided=IMembershipSource
        )

    def unregister_membership_source(self, adapter, interface, name):
        gsm = getGlobalSiteManager()
        gsm.unregisterAdapter(
            required=(interface,), name=name, provided=IMembershipSource
        )

    @contextmanager
    def custom_source(self, source):
        self.register_membership_source(source, Interface, 'custom-source')
        yield
        self.unregister_membership_source(source, Interface, 'custom-source')

    def get_test_person(self):
        person_type = self.new_temporary_type(
            behaviors=[IPerson.__identifier__],
            klass='seantis.people.types.base.PersonBase'
        )

        with self.user('admin'):
            person = api.content.create(
                title='person',
                type=person_type.id,
                container=self.new_temporary_folder()
            )

        return person

    def test_membership_adapter_registration(self):

        class Source(TestAdapter):

            def memberships(self, person=None):
                pass

        with self.custom_source(Source):

            folder = self.new_temporary_folder()

            adapters = [
                name for name, source in
                getAdapters((folder, ), IMembershipSource)
            ]

            self.assertEqual(
                adapters, ['zodb-membership-source', 'custom-source']
            )

        adapters = [
            name for name, source in
            getAdapters((folder, ), IMembershipSource)
        ]
        self.assertEqual(adapters, ['zodb-membership-source'])

    def test_membership_organizations(self):

        person = self.get_test_person()
        organization = self.new_temporary_folder()

        class Source(TestAdapter):

            def memberships(self, person=None):
                return {
                    IUUID(organization): [
                        Membership(person)
                    ]
                }

        with self.custom_source(Source):
            self.assertEqual(IPerson(person).organizations(), [
                organization.title
            ])

            self.assertEqual(IPerson(person).organization_uuids(), UUIDList([
                IUUID(organization)
            ]))

    def test_current_role(self):
        person = self.get_test_person()
        organization = self.new_temporary_folder()

        class Source(TestAdapter):

            def memberships(self, person=None):
                return {
                    IUUID(organization): [
                        Membership(person, 'president'),
                        Membership(person, 'secretary')
                    ]
                }

        with self.custom_source(Source):
            memberships = IPerson(person).memberships()[IUUID(organization)]
            role = IPerson(person).current_role(memberships)

            self.assertEqual(role, 'president')

    def test_membership_changed(self):
        tools.add_attribute_to_metadata('organizations', catalog_id)

        organization = self.new_temporary_folder()

        person = self.get_test_person()
        memberships = [Membership(person, 'vice-president')]

        class Source(TestAdapter):

            def memberships(self, person=None):
                return {IUUID(organization): memberships}

        with self.custom_source(Source):
            catalog = api.portal.get_tool(catalog_id)
            rid = tools.get_brain_by_object(person, catalog_id).getRID()

            get_orgs = lambda: catalog.getMetadataForRID(rid)['organizations']

            # because the membership source was added after the person
            # was created, the organizations metadata column is empty
            self.assertEqual(get_orgs(), [])

            # after signalling that the membership has changed, the
            # organizations should be available
            notify(MembershipChangedEvent(person))
            self.assertEqual(get_orgs(), [organization.id])
