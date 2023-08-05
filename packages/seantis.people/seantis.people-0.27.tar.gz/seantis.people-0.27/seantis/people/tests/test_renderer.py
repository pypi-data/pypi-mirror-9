from collections import namedtuple
from datetime import date, datetime
from mock import patch, MagicMock

from zope.interface import directlyProvides
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from Products.ZCatalog.interfaces import ICatalogBrain

from plone.supermodel import loadString
from plone.namedfile.file import NamedImage
from plone.app.textfield.value import RichTextValue
from plone.uuid.interfaces import IUUID

from seantis.people.browser.renderer import Renderer
from seantis.people.utils import UUIDList, LinkList
from seantis.people import tests


class TestRenderer(tests.IntegrationTestCase):

    model = """<?xml version='1.0' encoding='utf8'?>
    <model xmlns="http://namespaces.plone.org/supermodel/schema">
        <schema>
            <field name="textline"
                   type="zope.schema.TextLine">
                <title>Textline</title>
            </field>
            <field name="text"
                   type="zope.schema.Text">
                <title>Text</title>
            </field>
            <field name="email"
                   type="seantis.plonetools.schemafields.Email">
                <title>Email</title>
            </field>
            <field name="richtext"
                    type="plone.app.textfield.RichText">
                <title>Richtext</title>
            </field>
            <field name="website"
                   type="seantis.plonetools.schemafields.Website">
                <title>Website</title>
            </field>
            <field name="blobimage"
                   type="plone.namedfile.field.NamedBlobImage">
                <title>Blobimage</title>
            </field>
            <field name="image"
                   type="plone.namedfile.field.NamedImage">
                <title>Image</title>
            </field>
            <field name="date"
                   type="zope.schema.Date">
                <title>Date</title>
            </field>
            <field name="datetime"
                   type="zope.schema.Datetime">
                <title>Datetime</title>
            </field>
            <field name="list" type="zope.schema.Set">
              <title>List</title>
              <value_type type="zope.schema.Choice">
                <values>
                  <element>One</element>
                  <element>Two</element>
                  <element>Three</element>
                </values>
              </value_type>
            </field>
            <field name="choice" type="zope.schema.Choice">
                <title>Choice</title>
                <vocabulary>TestVocabulary</vocabulary>
            </field>
        </schema>
    </model>"""

    @property
    def schema(self):
        return loadString(self.model).schema

    def render_value(self, field, value):
        renderer = Renderer(self.schema, place='list')
        context = namedtuple('MockContext', [field])(value)
        return renderer.render(context, field)

    def test_textline(self):
        self.assertEqual(self.render_value('textline', u'test'), u'test')

    def test_email(self):
        self.assertEqual(
            self.render_value('email', u'test@example.com'),
            u'<a href="mailto:test@example.com">test@example.com</a>'
        )
        self.assertEqual(self.render_value('email', None), u'')

    def test_website(self):
        self.assertEqual(
            self.render_value('website', u'http://example.com'),
            (
                u'<a href="http://example.com" '
                u'target="_blank">http://example.com</a>'
            )
        )
        self.assertEqual(self.render_value('website', None), u'')

    def test_text(self):
        self.assertEqual(
            self.render_value('text', 'One\nTwo'),
            u'One<br />Two'
        )
        self.assertEqual(
            self.render_value('text', 'One\r\nTwo'),
            u'One<br />Two'
        )

    def test_richtext(self):
        text = RichTextValue(raw="<b>This is important</b>")

        self.assertEqual(
            self.render_value('richtext', text),
            u'<b>This is important</b>'
        )

    def test_date(self):
        self.assertEqual(
            self.render_value('date', date(2014, 12, 15)),
            u'Dec 15, 2014'
        )

    def test_datetime(self):
        self.assertEqual(
            self.render_value('datetime', datetime(2014, 12, 15, 12, 0)),
            u'Dec 15, 2014 12:00 PM'
        )

    def test_image(self):

        renderer = Renderer(self.schema, place='list')

        class MockContext(object):
            def getURL(self):
                return u'http://nohost/mockbrain'

            def absolute_url(self):
                return u'http://nohost/mockobject'

        context = MockContext()
        context.image = None
        self.assertEqual(renderer.render(context, 'image'), '')

        # if the context does not provide ICatalogBrain, absolute_url is used
        context.image = NamedImage()
        self.assertEqual(
            renderer.render(context, 'image'),
            u'<img src="http://nohost/mockobject/@@images/image/tile" />'
        )

        # per default, the size on the detail view is different
        renderer = Renderer(self.schema, place='detail')
        self.assertEqual(
            renderer.render(context, 'image'),
            u'<img src="http://nohost/mockobject/@@images/image/mini" />'
        )

        # if the context provides ICatalogBrain, getURL is used
        directlyProvides(context, ICatalogBrain)
        self.assertEqual(
            renderer.render(context, 'image'),
            u'<img src="http://nohost/mockbrain/@@images/image/mini" />'
        )

    def test_uuid_list(self):
        self.assertEqual(self.render_value('uuids', UUIDList()), u'')

        folders = (self.new_temporary_folder(), self.new_temporary_folder())
        uuids = UUIDList(IUUID(folder) for folder in folders)

        self.assertIn(folders[0].title, self.render_value('uuids', uuids))
        self.assertIn(folders[1].title, self.render_value('uuids', uuids))
        self.assertIn(
            folders[0].absolute_url(), self.render_value('uuids', uuids)
        )
        self.assertIn(
            folders[1].absolute_url(), self.render_value('uuids', uuids)
        )

    def test_link_list(self):
        self.assertEqual(self.render_value('links', LinkList()), u'')

        links = LinkList([
            (u'Google', 'https://www.google.ch'),
            (u'Bing', 'http://lmgtfy.com/?q=bing')
        ])

        self.assertIn(
            u'<li><a href="https://www.google.ch">Google</a></li>',
            self.render_value('links', links)
        )

        self.assertIn(
            u'<li><a href="http://lmgtfy.com/?q=bing">Bing</a></li>',
            self.render_value('links', links)
        )

    @patch('zope.component.getUtility')
    @patch('seantis.plonetools.tools.get_schema_from_portal_type')
    def test_choice(self, get_schema, get_utility):

        class MockUtililty(object):
            def __call__(self, name):
                return SimpleVocabulary([
                    SimpleTerm(value='1st', title=u'first'),
                    SimpleTerm(value='2nd', title=u'second'),
                ])

        get_schema.return_value = self.schema
        get_utility.return_value = MockUtililty()

        renderer = Renderer(self.schema, place='list')

        context = MagicMock()
        context.portal_type = 'portal_type'
        context.choice = '1st'
        self.assertEqual(renderer.render(context, 'choice'), u'first')

        context.choice = '2nd'
        self.assertEqual(renderer.render(context, 'choice'), u'second')
