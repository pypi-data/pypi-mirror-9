import json

from lxml import etree

from plone.autoform.widgets import WidgetExportImportHandler
from plone.supermodel.utils import noNS


class JsonWidgetExportImportHandler(WidgetExportImportHandler):
    """ plone.autoform widget attributes handler. May be given an arbitrary
    amount of attributes used on a widget, together with the expected type.

    The values are then parsed and stored as JSON.

    For example, the following xml...

    <field name="birthday" type="zope.schema.Date">
      <form:widget type="plone.formwidget.datetime.z3cform.widget.DateWidget">
        <years_range>[-100, 10]</years_range>
      </form:widget>
    </field>

    ...together with the following setup...

    Handler = JsonWidgetExportImportHandler({
        'years_range': tuple
    })

    ...will ensure that the years_range in json is read from the xml and used
    as widget parameter in json.

    """

    def __init__(self, attributes):
        self.attributes = attributes

    def read(self, widget_node, params):

        # get all child node attributes in one swoop
        child_nodes = dict(
            (noNS(c.tag), c.text.strip()) for c in widget_node.iterchildren()
            if noNS(c.tag) in self.attributes
        )

        for attr, value in child_nodes.items():
            params[attr] = self.attributes[attr](json.loads(value))

    def write(self, widget_node, params):
        for attribute in self.attributes:
            if params.get(attribute) is not None:
                child = etree.Element(attribute)
                child.text = json.dumps(params.get(attribute))
                widget_node.append(child)


DateWidgetExportImportHandler = JsonWidgetExportImportHandler({
    'years_range': tuple
})
