from mock import patch

from zope import schema
from plone.dexterity.content import Container
from plone.supermodel import loadString

from seantis.people import tests
from seantis.people.content.export_content import get_value


class TestExportContent(tests.IntegrationTestCase):

    @patch('zope.component.getUtility')
    @patch('seantis.plonetools.tools.get_schema_from_portal_type')
    def test_get_value(self, get_schema, get_utility):
        model = """<?xml version='1.0' encoding='utf8'?>
        <model xmlns="http://namespaces.plone.org/supermodel/schema">
            <schema>
                <field name="text" type="zope.schema.TextLine">
                </field>
                <field name="choice" type="zope.schema.Choice">
                    <vocabulary>vocabulary</vocabulary>
                </field>
            </schema>
        </model>"""
        vocabulary = schema.vocabulary.SimpleVocabulary([
            schema.vocabulary.SimpleTerm(value='1st', title=u'first'),
            schema.vocabulary.SimpleTerm(value='2nd', title=u'second')
        ])

        class MockUtililty(object):
            def __call__(self, name):
                return vocabulary

        get_schema.return_value = loadString(model).schema
        get_utility.return_value = MockUtililty()

        class TestPerson(Container):
            pass

        person = TestPerson()
        person.choice = '1st'
        person.text = 'test'
        self.assertEquals(u'test', get_value(self.request, person, 'text'))
        self.assertEquals(u'first', get_value(self.request, person, 'choice'))

        person.choice = '2nd'
        self.assertEquals(u'second', get_value(self.request, person, 'choice'))
