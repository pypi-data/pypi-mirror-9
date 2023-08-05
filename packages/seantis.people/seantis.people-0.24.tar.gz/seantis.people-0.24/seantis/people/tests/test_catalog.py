from datetime import datetime
from plone import api
from seantis.people import tests
from seantis.people.interfaces import IPerson
from seantis.people.supermodel import set_columns
from seantis.people.supermodel.indexing import on_type_modified


class TestCatalog(tests.IntegrationTestCase):

    def test_require_baseclass(self):
        without_baseclass = self.new_temporary_type(
            behaviors=[IPerson.__identifier__],
        )
        with_baseclass = self.new_temporary_type(
            behaviors=[IPerson.__identifier__],
            klass='seantis.people.types.base.PersonBase'
        )

        on_type_modified(without_baseclass)
        on_type_modified(with_baseclass)

        # create one object with the correct baseclass, one without.
        # Both are going to be in portal_catalog, but the one with the
        # person baseclass will end up in the people catalog only.
        with self.user('admin'):
            container = self.new_temporary_folder()
            api.content.create(
                id='without-baseclass',
                type=without_baseclass.id,
                container=container
            )
            api.content.create(
                id='with-baseclass',
                type=with_baseclass.id,
                container=container
            )

        path = '/'.join(container.getPhysicalPath())
        portal_catalog = api.portal.get_tool('portal_catalog')
        people_catalog = api.portal.get_tool('seantis_people_catalog')

        self.assertEqual(
            [b.id for b in portal_catalog(path={'query': path, 'depth': 1})],
            ['without-baseclass', 'with-baseclass']
        )

        self.assertEqual(
            [b.id for b in people_catalog(path={'query': path, 'depth': 1})],
            ['with-baseclass']
        )

    def test_column_metadata(self):
        new_type = self.new_temporary_type(
            behaviors=[IPerson.__identifier__],
            klass='seantis.people.types.base.PersonBase'
        )

        set_columns(new_type.lookupSchema(), [['foo']])
        on_type_modified(new_type)

        with self.user('admin'):
            api.content.create(
                id='123',
                type=new_type.id,
                container=self.new_temporary_folder(),
                foo='bar',
            )

        portal_catalog = api.portal.get_tool('portal_catalog')
        people_catalog = api.portal.get_tool('seantis_people_catalog')

        with self.assertRaises(AttributeError):
            portal_catalog(portal_type=new_type.id)[0].foo

        self.assertEqual(people_catalog(portal_type=new_type.id)[0].foo, 'bar')

    def test_default_indexes(self):
        new_type = self.new_temporary_type(
            behaviors=[IPerson.__identifier__],
            klass='seantis.people.types.base.PersonBase'
        )

        set_columns(new_type.lookupSchema(), [['foo']])
        on_type_modified(new_type)

        with self.user('admin'):
            created = datetime.now()

            api.content.create(
                id='007',
                type=new_type.id,
                container=self.new_temporary_folder(),
                Subject='O O Seven',
                title='James Bond',
                description='Spy for his Majesty, the Queen',
                created=created
            )

        portal_catalog = api.portal.get_tool('portal_catalog')
        people_catalog = api.portal.get_tool('seantis_people_catalog')

        portal_brain = portal_catalog(portal_type=new_type.id)[0]
        people_brain = people_catalog(portal_type=new_type.id)[0]

        self.assertEqual(portal_brain.id, '007')
        self.assertEqual(portal_brain.Subject, 'O O Seven')
        self.assertEqual(portal_brain.Title, 'James Bond')
        self.assertEqual(portal_brain.created, created)
        self.assertEqual(
            portal_brain.Description, 'Spy for his Majesty, the Queen'
        )

        self.assertEqual(portal_brain.id, people_brain.id)
        self.assertEqual(portal_brain.Title, people_brain.Title)
        self.assertEqual(portal_brain.Subject, people_brain.Subject)
        self.assertEqual(portal_brain.created, people_brain.created)
        self.assertEqual(portal_brain.Description, people_brain.Description)

        self.assertEqual(len(portal_catalog(Subject='O O Seven')), 1)
        self.assertEqual(len(people_catalog(Subject='O O Seven')), 1)

        self.assertEqual(len(portal_catalog(SearchableText='James Bond')), 1)
        self.assertEqual(len(people_catalog(SearchableText='James Bond')), 1)

        # folder and person
        self.assertEqual(len(portal_catalog(created=created)), 2)

        # person only
        self.assertEqual(len(people_catalog(created=created)), 1)
