from zope.component import getAdapters
from plone import api

from seantis.plonetools import tools
from seantis.people.interfaces import ICompoundColumns
from seantis.people.supermodel.security import has_read_access
from seantis.people.supermodel import (
    get_columns,
    get_custom_column_titles,
    get_selectable_fields,
    get_title_fields,
)


# Compound columns are columns where the key is used for filtering and the
# value is used for display. For example, the organizations column contains
# the name of the organizations a person belongs to, but to render these
# in the list, the organization_uuids attribute is used which being rendered
# with links to the actual organizations.
def get_compound_columns():
    columns = {
        'organizations': 'organization_uuids'
    }
    for name, adapter in getAdapters((api.portal.get(), ), ICompoundColumns):
        columns.update(adapter.get_compound_columns())

    return columns


def unrestricted_get_schema_columns(schema):
    return _get_schema_columns(schema, None, restricted=False)


def get_schema_columns(schema, context):
    return _get_schema_columns(schema, context, restricted=True)


def _get_schema_columns(schema, context, restricted):
    columns = []
    titles = get_custom_column_titles(schema)

    for ix, fields in enumerate(get_columns(schema)):
        if restricted:
            fields = [
                f for f in fields if has_read_access(schema, f, context)
            ]

        if fields:
            columns.append(SchemaColumn(schema, fields, titles[ix]))

    return columns


class SchemaColumn(object):

    def __init__(self, schema, fields, custom_title=None):
        self.schema = schema
        self.fields = tools.order_fields_by_schema(fields, schema)

        if custom_title is not None:
            self.titles = [custom_title]
        else:
            self.titles = []
            for field in self.fields:
                if field in self.schema:
                    self.titles.append(self.schema[field].title)
                else:
                    self.titles.append(field)

        self.contains_title_field = bool(
            set(self.fields) & set(get_title_fields(self.schema))
        )
        self.selectable = (
            len(self.fields) == 1 and self.fields[0] in get_selectable_fields(
                self.schema
            )
        )
        self.filter_key = self.selectable and self.fields[0] or None
