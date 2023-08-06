from plone import api

from seantis.people.interfaces import IPerson

from seantis.people.supermodel import set_detail_fields
from seantis.people import tests


class TestList(tests.IntegrationTestCase):

    def test_person_view_positions(self):
        with self.user('admin'):
            person_type = self.new_temporary_type(
                behaviors=[IPerson.__identifier__],
                klass='seantis.people.types.base.PersonBase'
            )
            person = api.content.create(
                id='test',
                type=person_type.id,
                container=self.new_temporary_folder(),
                name='test',
                town='test',
                empty=''
            )
            schema = person_type.lookupSchema()
            view = person.unrestrictedTraverse('@@view')

        set_detail_fields(schema, {'top': ['name'], 'left': ['empty']})

        # empty positions are not visible and are therefore left out completely
        self.assertEqual(view.visible_positions(), ['top'])

        # split screen is available only if left and right are available
        self.assertFalse(view.split_screen())

        set_detail_fields(schema, {'left': ['name'], 'right': ['town']})

        self.assertEqual(view.visible_positions(), ['left', 'right'])
        self.assertTrue(view.split_screen())

    def test_person_view_navigation(self):
        with self.user('admin'):
            lst = api.content.create(
                id='test',
                type='seantis.people.list',
                container=self.new_temporary_folder()
            )
            person_type = self.new_temporary_type(
                behaviors=[IPerson.__identifier__],
                klass='seantis.people.types.base.PersonBase'
            )
            one = api.content.create(
                id='one',
                type=person_type.id,
                container=lst,
                name='test',
                town='test',
                empty=''
            )

            view = one.unrestrictedTraverse('@@view')
            self.assertEqual(view.get_adjacent_urls(), (None, None))

            two = api.content.create(
                id='two',
                type=person_type.id,
                container=lst,
                name='test',
                town='test',
                empty=''
            )

            view = one.unrestrictedTraverse('@@view')
            self.assertEqual(
                view.get_adjacent_urls(), (None, two.absolute_url())
            )

            view = two.unrestrictedTraverse('@@view')
            self.assertEqual(
                view.get_adjacent_urls(), (one.absolute_url(), None)
            )

            three = api.content.create(
                id='three',
                type=person_type.id,
                container=lst,
                name='test',
                town='test',
                empty=''
            )

            view = two.unrestrictedTraverse('@@view')
            self.assertEqual(
                view.get_adjacent_urls(), (
                    one.absolute_url(), three.absolute_url()
                )
            )

    def test_custom_titles(self):
        with self.user('admin'):
            person_type = self.new_temporary_type(
                behaviors=[IPerson.__identifier__],
                klass='seantis.people.types.base.PersonBase'
            )
            person = api.content.create(
                id='test',
                type=person_type.id,
                container=self.new_temporary_folder(),
                name='test',
                town='test',
                empty=''
            )
            view = person.unrestrictedTraverse('@@view')

        self.assertEqual(view.get_field_title('name'), u'name')

        person.custom_titles = {
            'name': u'Nom'
        }

        self.assertEqual(view.get_field_title('name'), u'Nom')
