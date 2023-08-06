from datetime import date, time, datetime

import isodate
import tablib

import zope
from zope.i18nmessageid.message import Message
from zope.schema.interfaces import IVocabularyFactory

from plone import api
from plone.app.textfield.value import RichTextValue
from plone.namedfile.file import NamedImage, NamedBlobImage

from seantis.plonetools import tools
from seantis.people import _
from seantis.people import catalog_id
from seantis.people.errors import ContentExportError


supported_formats = [
    'csv',
    'json',
    'xls',
    'xlsx'
]


def export_people(request, container, portal_type, fields,
                  review_state=None, include_inactive=True):

    people = get_people(container, portal_type, review_state, include_inactive)

    if not people:
        raise ContentExportError(_(u"No people to export"))

    records = (get_record(request, person, fields) for person in people)

    translate = tools.translator(request, 'seantis.people')
    dataset = tablib.Dataset(headers=[translate(f[1]) for f in fields])
    map(dataset.append, records)

    return dataset


def get_people(container, portal_type,
               review_state=None, include_inactive=True):

    catalog = api.portal.get_tool(catalog_id)
    path = '/'.join(container.getPhysicalPath())

    query = {
        'path': path,
        'portal_type': portal_type,
    }

    if review_state is not None:
        query['review_state'] = review_state

    if not include_inactive:
        query['is_active_person'] = True

    return [b.getObject() for b in catalog(query)]


def get_record(request, person, fields):
    record = []

    translate = tools.translator(request, 'seantis.people')

    for field in (get_field(request, person, f[0]) for f in fields):
        if isinstance(field, Message):
            record.append(translate(field))
        else:
            record.append(field)

    return record


def get_value(request, person, field):
    value = getattr(person, field)

    schema = tools.get_schema_from_portal_type(person.portal_type)
    try:
        name = schema.get(field).vocabularyName
    except AttributeError:
        return getattr(person, field)

    vocabulary = zope.component.getUtility(IVocabularyFactory, name)(person)
    try:
        translate = tools.translator(request, 'seantis.people')
        return translate(vocabulary.getTerm(value).title)

    except LookupError:
        return value


def get_field(request, person, field):

    if not hasattr(person, field):
        raise ContentExportError(_(u"Field '${name}' does not exist", mapping={
            'name': field
        }))

    value = get_value(request, person, field)

    if value is None:
        return u''

    if isinstance(value, bool):
        return _(u'Yes') if value is True else _(u'No')

    if isinstance(value, basestring):
        return unicode(value)

    if field in person.membership_fields.keys():
        organizations = (api.content.get(UID=i).title for i in value.keys())
        return u', '.join(organizations)

    if isinstance(value, (list, tuple, set)):
        return u', '.join(value)

    if isinstance(value, dict):
        parts = []
        for key in sorted(value):
            parts.append(u'{}: {}'.format(key, value[key]))
        return u', '.join(parts)

    if isinstance(value, date):
        return unicode(isodate.date_isoformat(value))

    if isinstance(value, datetime):
        return unicode(isodate.datetime_isoformat(value))

    if isinstance(value, time):
        return unicode(isodate.time_isoformat(value))

    if isinstance(value, RichTextValue):
        return unicode(value.output)

    if isinstance(value, (NamedImage, NamedBlobImage)):
        base = person.absolute_url()

        if value.filename:
            return u'{}/@@download/{}/{}'.format(base, field, value.filename)
        else:
            return u'{}/@@download/{}'.format(base, field)

    return value
