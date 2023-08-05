# -*- coding: utf-8 -*-

from plone import api

from seantis.plonetools import tools

from seantis.people import catalog_id
from seantis.people import tests
from seantis.people.interfaces import IPerson
from seantis.people.supermodel import (
    set_selectable_fields, set_columns, get_compound_columns
)

from seantis.people.supermodel.indexing import (
    update_related_indexes,
    update_metadata
)


class TestIndex(tests.IntegrationTestCase):

    selectable_xml = """<?xml version='1.0' encoding='utf8'?>
        <model  xmlns="http://namespaces.plone.org/supermodel/schema"
                xmlns:people="http://namespaces.plone.org/supermodel/people">
            <schema>
                <people:columns>
                    <people:column selectable="true">
                        <people:item>first</people:item>
                    </people:column>
                    <people:column selectable="true">
                        <people:item>second</people:item>
                    </people:column>
                    <people:column selectable="true">
                        <people:item>third</people:item>
                    </people:column>

                </people:columns>
            </schema>
        </model>"""

    def test_selectable_fields_index(self):
        new_type = self.new_temporary_type(
            behaviors=[IPerson.__identifier__],
            model_source=self.selectable_xml,
            klass='seantis.people.types.base.PersonBase'
        )
        schema = new_type.lookupSchema()

        catalog = api.portal.get_tool(catalog_id)

        ix = '{}_selectable_{}'

        self.assertIn(ix.format(new_type.id, 'first'), catalog.indexes())
        self.assertIn(ix.format(new_type.id, 'second'), catalog.indexes())
        self.assertIn(ix.format(new_type.id, 'third'), catalog.indexes())

        # nothing changes implicitly
        set_selectable_fields(schema, ['third'])

        self.assertIn(ix.format(new_type.id, 'first'), catalog.indexes())
        self.assertIn(ix.format(new_type.id, 'second'), catalog.indexes())
        self.assertIn(ix.format(new_type.id, 'third'), catalog.indexes())

        # the index must be rebuilt by hand (using the web-interface events
        # will take care of that)
        update_related_indexes(new_type)

        self.assertNotIn(ix.format(new_type.id, 'first'), catalog.indexes())
        self.assertNotIn(ix.format(new_type.id, 'second'), catalog.indexes())
        self.assertIn(ix.format(new_type.id, 'third'), catalog.indexes())

    def test_first_letter_index(self):
        self.login('admin')

        new_type = self.new_temporary_type(
            behaviors=[IPerson.__identifier__],
            klass='seantis.people.types.base.PersonBase'
        )
        folder = self.new_temporary_folder()

        create = lambda title: api.content.create(
            title=title, type=new_type.id, container=folder
        )

        objects = [create(name) for name in (
            u'Andrew', u'Beat', u'cesar', u'Dexter', u'', u'ändu', u'Ödipus'
        )]

        catalog = api.portal.get_tool(catalog_id)
        index = catalog._catalog.getIndex('first_letter')

        values = [
            index.getEntryForObject(
                tools.get_brain_by_object(obj, catalog_id).getRID()
            ) for obj in objects
        ]

        self.assertEqual(sorted(values), [
            u'', u'A', u'B', u'C', u'D', u'Ä', u'Ö'
        ])

    def test_first_letter_index_update(self):
        foobar_xml = """<?xml version='1.0' encoding='utf8'?>
        <model xmlns="http://namespaces.plone.org/supermodel/schema"
               xmlns:people="http://namespaces.plone.org/supermodel/people">
                <schema>
                    <people:order>
                        <people:item>foo</people:item>
                        <people:item>bar</people:item>
                    </people:order>
                </schema>
        </model>"""
        self.login('admin')

        foobar = self.new_temporary_type(
            behaviors=[IPerson.__identifier__],
            model_source=foobar_xml,
            klass='seantis.people.types.base.PersonBase'
        )

        obj = api.content.create(
            title='test',
            type=foobar.id,
            container=self.new_temporary_folder()
        )

        catalog = api.portal.get_tool(catalog_id)

        index = catalog._catalog.getIndex('first_letter')

        get_index_value = lambda: index.getEntryForObject(
            tools.get_brain_by_object(obj, catalog_id).getRID()
        )

        self.assertEqual(get_index_value(), u'T')

        obj.title = 'asdf'
        obj.reindexObject()
        self.assertEqual(get_index_value(), u'A')

        obj.bar = 'bar'
        obj.reindexObject()
        self.assertEqual(get_index_value(), u'B')

        obj.foo = u'ähm'
        obj.reindexObject()
        self.assertEqual(get_index_value(), u'Ä')

    def test_compound_columns_metadata(self):
        # Both key and value of a compound_column are added to the metadata
        # if the key alone is added.

        new_type = self.new_temporary_type(behaviors=[IPerson.__identifier__])

        compound_columns = get_compound_columns()
        columns = [[key] for key in compound_columns]
        set_columns(new_type.lookupSchema(), columns)

        catalog = api.portal.get_tool(catalog_id)

        # the sets are completely different, the compound keys/values are not
        # part of the catalog columns
        self.assertFalse(
            set(compound_columns.keys()) & set(catalog._catalog.names)
        )
        self.assertFalse(
            set(compound_columns.values()) & set(catalog._catalog.names)
        )

        update_metadata(new_type)

        # the compound keys/values are a subset of the catalog columns
        self.assertTrue(
            set(compound_columns.keys()) <= set(catalog._catalog.names)
        )
        self.assertTrue(
            set(compound_columns.values()) <= set(catalog._catalog.names)
        )
