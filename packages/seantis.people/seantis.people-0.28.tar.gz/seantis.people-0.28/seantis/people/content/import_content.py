import logging
log = logging.getLogger('seantis.people')

from urllib import urlopen
from collections import namedtuple

import tablib

from plone import api
from plone import namedfile

import zope
from zope.schema import getFields, getValidationErrors, Text
from zope.schema._bootstrapinterfaces import RequiredMissing
from zope.schema.interfaces import (
    IFromUnicode, ValidationError, SchemaNotFullyImplemented,
    IDate, IDatetime, IURI, ITextLine, IList, ISet, IChoice,
    IVocabularyFactory
)

from isodate import parse_date, parse_datetime

from seantis.people import _
from seantis.people.errors import ContentImportError
from seantis.plonetools import tools

supported_formats = ('csv', )


def import_people(request, container, portal_type, format, data):
    dataset = get_dataset(format, data)
    attribute_map = get_attribute_map(request, dataset.headers, portal_type)

    schema = tools.get_schema_from_portal_type(portal_type)

    for ix, record in enumerate(dataset.dict):
        log.info('processing row number {}'.format(ix+1))
        try:
            values = get_attribute_values(request, record, attribute_map)

            # add None for missing values
            for field in getFields(schema).keys():
                if field not in values:
                    values[field] = None

            validate_attribute_values(schema, values)

            api.content.create(
                container=container,
                type=portal_type,
                id='',
                **values
            )
        except ContentImportError, e:
            raise ContentImportError(
                e.message, rownumber=ix+1, colname=e.colname
            )
        except Exception, e:
            log.exception('error importing people')
            raise ContentImportError(e.message, rownumber=ix+1)

    return ix + 1


def get_dataset(format, data):
    assert format in supported_formats

    def get_dataset_from_csv():
        ds = tablib.Dataset()
        ds.csv = data

        return ds

    return locals()['get_dataset_from_{}'.format(format)]()


def get_attribute_map(request, headers, portal_type):

    if not headers:
        raise ContentImportError(_(u'No column headers were found'))

    schema = tools.get_schema_from_portal_type(portal_type)
    attribute_map = {}

    fields = getFields(schema)

    known_titles = dict((field.title, field) for field in fields.values())
    known_fields = dict((key, field) for key, field in fields.items())

    translate = tools.translator(request)
    known_translated_titles = dict(
        (translate(field.title), field) for field in fields.values()
    )

    for header in headers:

        if header in known_translated_titles:
            field = known_translated_titles[header]
        elif header in known_fields:
            field = known_fields[header]
        elif header in known_titles:
            field = known_titles[header]
        else:
            log.warn(u"The header '{}' was ignored.".format(header))
            continue

        if field in attribute_map.values():
            raise ContentImportError(
                _(
                    u'The ${name} column is specified more than once',
                    mapping=dict(name=header)
                )
            )

        if field in ('title', 'id'):
            raise ContentImportError(
                _(
                    u'The ${name} column is invalid. "title" and "id" are '
                    u'reserved fieldnames which may not be used.',
                    mapping=dict(name=header)
                )
            )

        attribute_map[header] = field

    return attribute_map


def get_vocabularies(request, attribute_map):
    """ Returns a dictionary containing all (translated) vocabularies used by
    the given attribute map.

    """
    vocabularies = {}
    translate = tools.translator(request)
    for header, field in attribute_map.items():
        if IChoice.providedBy(field):
            vocabulary = zope.component.getUtility(IVocabularyFactory,
                                                   field.vocabularyName)
            vocabulary = vocabulary(None)
            vocabularies[header] = dict([
                (translate(term.title).lower(), term.value)
                for term in vocabulary._terms
            ])

    return vocabularies


def download_field_from_url(field, url):
    """ Download the field from the given url if supported by the field.
    Returns False if the download does not apply to the given field. If None
    is returned, the value of the field actually is None.

    """

    downloadables = {
        namedfile.field.NamedImage: field._type,
        namedfile.field.NamedBlobImage: field._type
    }

    url = url.strip()

    # images are fetched through their url if possible
    for fieldtype, klass in downloadables.items():
        if isinstance(field, fieldtype):
            try:
                image = klass(urlopen(url.encode('utf-8')).read())
                if -1 in image.getImageSize():
                    return None
                else:
                    return image
            except IOError:
                return None

    return False


def convert_to_list(value):
    if '\n' in value:
        separator = '\n'
    else:
        separator = ','

    return [s.strip() for s in value.split(separator)]


def get_attribute_values(request, record, attribute_map):
    values = {}
    vocabularies = get_vocabularies(request, attribute_map)

    for header, field in attribute_map.items():

        downloaded = download_field_from_url(field, record[header])
        if downloaded is not False:
            values[field.__name__] = downloaded
            continue

        if IDate.providedBy(field):
            if not record[header]:
                values[field.__name__] = None
            else:
                values[field.__name__] = parse_date(record[header])
            continue

        if IDatetime.providedBy(field):
            if not record[header]:
                values[field.__name__] = None
            else:
                values[field.__name__] = parse_datetime(record[header])
            continue

        if IURI.providedBy(field):
            if not record[header].strip():
                values[field.__name__] = None
                continue

        if IList.providedBy(field):
            if ITextLine.providedBy(field.value_type):
                values[field.__name__] = convert_to_list(record[header])
                continue

        if ISet.providedBy(field):
            if IChoice.providedBy(field.value_type):
                values[field.__name__] = set(convert_to_list(record[header]))
                continue

        if IChoice.providedBy(field):
            if not record[header].strip():
                values[field.__name__] = None
            else:
                vocabulary = vocabularies[header]
                if record[header].lower() not in vocabulary:
                    raise ContentImportError(
                        _(
                            u'The ${name} column contains the '
                            u'unknown value ${value}',
                            mapping=dict(name=header, value=record[header])
                        )
                    )

                values[field.__name__] = vocabulary[record[header].lower()]

            continue

        assert IFromUnicode.providedBy(field), """
            {} does not support fromUnicode
        """.format(field)

        try:
            values[field.__name__] = field.fromUnicode(record[header])

            if isinstance(values[field.__name__], basestring):
                values[field.__name__] = values[field.__name__].strip()
            if isinstance(field, Text):
                values[field.__name__] = values[field.__name__].replace(
                    '<br />', '\n'
                )

        except ValidationError, e:
            raise ContentImportError(e.doc(), colname=header)
        except ValueError, e:
            raise ContentImportError(e.message, colname=header)

    return values


def validate_attribute_values(schema, values):
    obj = namedtuple('ImportObject', values.keys())(**values)

    for error in getValidationErrors(schema, obj):
        column = schema[error[0]].title

        if isinstance(error[1], (SchemaNotFullyImplemented, RequiredMissing)):
            raise ContentImportError(
                _(u'Required column is missing'), colname=column
            )
        else:
            raise ContentImportError(error, colname=column)
