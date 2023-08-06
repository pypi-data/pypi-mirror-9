# -*- coding: utf-8 -*-

from plone import api

from plone.uuid.interfaces import IUUID
from Products.CMFPlone.interfaces.constrains import IConstrainTypes, ENABLED

from seantis.people.interfaces import IPerson
from seantis.people.content import List
from seantis.people import tests
from seantis.people.content.list import ListConstrainTypes, LetterFilter
from seantis.people.utils import UUIDList

from pyquery import PyQuery as pq


class TestList(tests.IntegrationTestCase):

    def test_list_creation(self):
        with self.user('admin'):
            lst = api.content.create(
                id='test',
                type='seantis.people.list',
                container=self.new_temporary_folder()
            )

        self.assertIs(type(lst.aq_base), List)

    def test_list_people_by_behavior(self):
        with self.user('admin'):
            lst = api.content.create(
                id='test',
                type='seantis.people.list',
                container=self.new_temporary_folder()
            )

            new_person_type = lambda: self.new_temporary_type(
                behaviors=[IPerson.__identifier__],
                klass='seantis.people.types.base.PersonBase'
            )

            person = new_person_type()
            new_person_type()  # intentionally unused

            # all types are possible before any are used
            self.assertEqual(len(lst.possible_types()), 2)
            self.assertEqual(len(lst.available_types()), 2)
            self.assertEqual(lst.used_type(), None)

            api.content.create(id='ned', type=person.id, container=lst)
            api.content.create(id='robb', type=person.id, container=lst)

            # only one type is used at this point
            self.assertEqual(len(lst.people()), 2)
            self.assertEqual(len(lst.possible_types()), 2)
            self.assertEqual(len(lst.available_types()), 1)
            self.assertEqual(lst.used_type(), person)

    def test_list_constrain(self):
        with self.user('admin'):
            lst = api.content.create(
                id='test',
                type='seantis.people.list',
                container=self.new_temporary_folder()
            )
            constrain = IConstrainTypes(lst)

            new_type = self.new_temporary_type(
                behaviors=[IPerson.__identifier__],
                klass='seantis.people.types.base.PersonBase'
            )

            self.assertIs(type(constrain), ListConstrainTypes)
            self.assertEqual(constrain.getConstrainTypesMode(), ENABLED)
            self.assertEqual(constrain.allowedContentTypes(), [new_type])
            self.assertEqual(constrain.getLocallyAllowedTypes(), [new_type.id])
            self.assertEqual(
                constrain.getImmediatelyAddableTypes(), [new_type.id]
            )

    def test_add_unsupported_type(self):
        with self.user('admin'):
            lst = api.content.create(
                id='test',
                type='seantis.people.list',
                container=self.new_temporary_folder()
            )

            add_invalid_type = lambda: api.content.create(
                id='invalid', type=self.new_temporary_type(), container=lst
            )

        self.assertRaises(api.exc.InvalidParameterError, add_invalid_type)

    def test_list_letters(self):
        with self.user('admin'):
            lst = api.content.create(
                id='test',
                type='seantis.people.list',
                container=self.new_temporary_folder()
            )

            person = self.new_temporary_type(
                behaviors=[IPerson.__identifier__],
                klass='seantis.people.types.base.PersonBase'
            )

            api.content.create(title='Jessie', type=person.id, container=lst)
            api.content.create(title='Walt', type=person.id, container=lst)

        self.assertEqual(sorted(lst.letters()), ['J', 'W'])

        filtered = lst.people(filter=LetterFilter('J', None))
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].id, 'jessie')

    def test_list_inactive(self):
        with self.user('admin'):
            lst = api.content.create(
                id='test',
                type='seantis.people.list',
                container=self.new_temporary_folder()
            )

            person = self.new_temporary_type(
                behaviors=[IPerson.__identifier__],
                klass='seantis.people.types.base.PersonBase'
            )

            api.content.create(title='Abed', type=person.id, container=lst)
            api.content.create(
                title='Troy',
                type=person.id,
                container=lst,
                is_active_person=False
            )

        # admins see inactive people
        with self.user('admin'):
            self.assertEqual(len(lst.people()), 2)

        # normal users do not
        self.assertEqual(len(lst.people()), 1)

        # unless overriden by flag
        self.assertEqual(len(lst.people(include_inactive=True)), 2)

    def test_list_unrestricted(self):
        with self.user('admin'):
            lst = api.content.create(
                id='test',
                type='seantis.people.list',
                container=self.new_temporary_folder()
            )

            person = self.new_temporary_type(
                behaviors=[IPerson.__identifier__],
                klass='seantis.people.types.base.PersonBase'
            )

            workflows = api.portal.get_tool('portal_workflow')
            workflows.setChainForPortalTypes(
                [person.id], 'simple_publication_workflow'
            )

            abed = api.content.create(
                title='Abed', type=person.id, container=lst
            )

            self.assertEqual(len(lst.people()), 1)

        # we are no longer admin so we don't see the private people
        self.assertEqual(len(lst.people(unrestricted_search=False)), 0)

        # unless we request it
        self.assertEqual(len(lst.people(unrestricted_search=True)), 1)

        # or we publish
        with self.user('admin'):
            api.content.transition(obj=abed, transition='publish')

        self.assertEqual(len(lst.people()), 1)

    def test_list_view_empty(self):
        with self.user('admin'):
            lst = api.content.create(
                id='test',
                type='seantis.people.list',
                container=self.new_temporary_folder()
            )

            view = lst.unrestrictedTraverse('@@view')

        self.assertIn('No people in the list.', view())

    def test_list_view_columns(self):

        model = """<?xml version='1.0' encoding='utf8'?>
        <model
            xmlns="http://namespaces.plone.org/supermodel/schema"
            xmlns:people="http://namespaces.plone.org/supermodel/people"
        >
            <schema>
                <people:columns>
                    <people:column>
                        <people:item>firstname</people:item>
                    </people:column>
                    <people:column>
                        <people:item>lastname</people:item>
                    </people:column>
                </people:columns>
                <field name="firstname" type="zope.schema.TextLine">
                    <title>First name</title>
                </field>
                <field name="lastname" type="zope.schema.TextLine">
                    <title>Last name</title>
                </field>
            </schema>
        </model>"""

        with self.user('admin'):
            lst = api.content.create(
                id='test',
                type='seantis.people.list',
                container=self.new_temporary_folder(),
            )

            person = self.new_temporary_type(
                behaviors=[IPerson.__identifier__],
                model_source=model,
                klass='seantis.people.types.base.PersonBase'
            ).id

            api.content.create(
                id='miri', type=person, container=lst,
                firstname='Miriam', lastname='Linky'
            )
            api.content.create(
                id='zack', type=person, container=lst,
                firstname='Zack', lastname='Brown'
            )

            view = lst.unrestrictedTraverse('@@view')

        page = pq(view())

        self.assertEqual(len(page.find('thead th')), 2)

        self.assertEqual(len(page.find('tbody tr')), 2)
        self.assertEqual(len(page.find('tbody tr:first-child td')), 2)

        self.assertEqual(page.find('thead').text(), 'First name Last name')
        self.assertEqual(page.find('tbody').text(), 'Miriam Linky Zack Brown')

    def test_list_view_filter_multiple_values(self):
        model = """<?xml version='1.0' encoding='utf8'?>
        <model xmlns="http://namespaces.plone.org/supermodel/schema"
               xmlns:people="http://namespaces.plone.org/supermodel/people">
            <schema>
                <people:columns>
                    <people:column selectable="true">
                        <people:item>countries</people:item>
                    </people:column>
                </people:columns>
            </schema>
        </model>"""

        with self.user('admin'):
            lst = api.content.create(
                id='test',
                type='seantis.people.list',
                container=self.new_temporary_folder()
            )

            group = self.new_temporary_type(
                behaviors=[IPerson.__identifier__],
                model_source=model,
                klass='seantis.people.types.base.PersonBase'
            ).id

            countries = api.content.create(
                title='countries', type=group, container=lst, countries=[
                    'Germany', 'Switzerland'
                ]
            )

            view = lst.unrestrictedTraverse('@@view')

        columns = view.columns()

        view.request['filter-countries'] = 'Switzerland'

        self.assertEqual(len(view.people()), 1)
        self.assertEqual(view.column_values(columns[0]), countries.countries)
        self.assertEqual(view.selected_column_value(columns[0]), 'Switzerland')

        view.request['filter-countries'] = 'France'

        self.assertEqual(len(view.people()), 0)
        self.assertEqual(view.column_values(columns[0]), countries.countries)
        self.assertEqual(view.selected_column_value(columns[0]), 'France')

    def test_list_view_filter(self):

        model = """<?xml version='1.0' encoding='utf8'?>
        <model xmlns="http://namespaces.plone.org/supermodel/schema"
               xmlns:people="http://namespaces.plone.org/supermodel/people">
            <schema>
                <people:columns>
                    <people:column selectable="true">
                        <people:item>country</people:item>
                    </people:column>
                </people:columns>
                <field name="country" type="zope.schema.TextLine">
                    <title>Country</title>
                </field>
            </schema>
        </model>"""

        with self.user('admin'):
            lst = api.content.create(
                id='test',
                type='seantis.people.list',
                container=self.new_temporary_folder(),
            )

            country = self.new_temporary_type(
                behaviors=[IPerson.__identifier__],
                model_source=model,
                klass='seantis.people.types.base.PersonBase'
            ).id

            countries = [u'Österreich', u'Germany', u'Switzerland']
            enc_countries = [c.encode('utf-8') for c in countries]

            for c in countries:
                api.content.create(
                    title=c, type=country, container=lst, country=c
                )

            view = lst.unrestrictedTraverse('@@view')

        columns = view.columns()

        self.assertEqual(len(view.people()), 3)
        self.assertEqual(len(columns), 1)
        self.assertEqual(view.column_values(columns[0]), enc_countries)
        self.assertEqual(view.selected_column_value(columns[0]), '__all__')

        view.request['filter-country'] = 'Switzerland'

        self.assertEqual(len(view.people()), 1)
        self.assertEqual(view.column_values(columns[0]), enc_countries)
        self.assertEqual(view.selected_column_value(columns[0]), 'Switzerland')

        view.request['filter-country'] = 'Österreich'

        self.assertEqual(len(view.people()), 1)
        self.assertEqual(view.column_values(columns[0]), enc_countries)
        self.assertEqual(view.selected_column_value(columns[0]), 'Österreich')

    def test_list_view_compound_column_organizations(self):

        model = """<?xml version='1.0' encoding='utf8'?>
        <model xmlns="http://namespaces.plone.org/supermodel/schema"
               xmlns:people="http://namespaces.plone.org/supermodel/people">
            <schema>
                <people:columns>
                    <people:column selectable="true">
                        <people:item>organizations</people:item>
                    </people:column>
                </people:columns>
            </schema>
        </model>"""

        with self.user('admin'):
            lst = api.content.create(
                id='test',
                type='seantis.people.list',
                container=self.new_temporary_folder(),
            )

            person = self.new_temporary_type(
                behaviors=[IPerson.__identifier__],
                model_source=model,
                klass='seantis.people.types.base.PersonBase'
            ).id

            organizations = [
                self.new_temporary_folder(),
                self.new_temporary_folder()
            ]

            # normally organizations are defined through memberships,
            # but it's easier here to just use class properties
            #
            # XXX -> this should be changed to really setup memberships, so
            # the testcode in PersonBase is not needed!
            api.content.create(
                title='test', type=person, container=lst,
                test_organizations=[o.title for o in organizations],
                test_organization_uuids=UUIDList(
                    [IUUID(o) for o in organizations]
                )
            )
            api.content.create(
                title='loner', type=person, container=lst,
                test_organizations=[], test_organization_uuids=UUIDList()
            )

            view = lst.unrestrictedTraverse('@@view')

        columns = view.columns()

        # no filter applied, both people shown
        self.assertEqual(len(view.people()), 2)

        # the select element contains the organizations
        self.assertEqual(
            view.column_values(columns[0]),
            sorted([o.title for o in organizations])
        )
        self.assertEqual(columns[0].filter_key, 'organizations')

        # the table contains the links to the organizations (from the uuids)
        page = pq(view())

        for org in organizations:
            link = page.find('.people-list a[href="{}"]'.format(
                org.absolute_url())
            )
            self.assertEqual(link.text(), org.title)

        # filtering the organizations happen without the uuids
        view.request['filter-organizations'] = organizations[0].title
        self.assertEqual(len(view.people()), 1)

    def test_list_view_schema(self):
        with self.user('admin'):
            lst = api.content.create(
                id='test',
                type='seantis.people.list',
                container=self.new_temporary_folder()
            )

            view = lst.unrestrictedTraverse('@@view')

        # don't call if there are no people
        self.assertRaises(AssertionError, lambda: view.schema)

        with self.user('admin'):
            person = self.new_temporary_type(
                behaviors=[IPerson.__identifier__],
                klass='seantis.people.types.base.PersonBase'
            )
            api.content.create(id='test', type=person.id, container=lst)

        self.assertEqual(view.schema, person.lookupSchema())

    def test_list_view_filter_property(self):
        with self.user('admin'):
            lst = api.content.create(
                id='test',
                type='seantis.people.list',
                container=self.new_temporary_folder()
            )

            view = lst.unrestrictedTraverse('@@view')

        self.assertEqual(view.filter, None)

        view.filter_prefix = 'test-filter-'
        view.request['test-filter-key'] = 'value'

        self.assertEqual(view.filter.key, 'key')
        self.assertEqual(view.filter.value, 'value')
        self.assertEqual(view.filter.title, u'')
