from plone.supermodel import loadString, serializeSchema

from seantis.people import tests


class TestSchemaColumns(tests.IntegrationTestCase):

    test_model = """<?xml version='1.0' encoding='utf8'?>
        <model xmlns="http://namespaces.plone.org/supermodel/schema"
               xmlns:form="http://namespaces.plone.org/supermodel/form">
          <schema>
            <field name="birthday" type="zope.schema.Date">
              <title>Go Shorty</title>
              <form:widget
                type="plone.formwidget.datetime.z3cform.widget.DateWidget">
                <years_range>[-100, 10]</years_range>
              </form:widget>
            </field>
          </schema>
        </model>"""

    def test_read_widget(self):
        model = loadString(self.test_model)
        widgets = model.schema.getTaggedValue('plone.autoform.widgets')

        self.assertEqual(
            widgets['birthday'].params, {'years_range': (-100, 10)}
        )

    def test_write_widget(self):
        model = loadString(self.test_model)
        xml = serializeSchema(model.schema)

        self.assertIn('<years_range>[-100, 10]</years_range>', xml)
