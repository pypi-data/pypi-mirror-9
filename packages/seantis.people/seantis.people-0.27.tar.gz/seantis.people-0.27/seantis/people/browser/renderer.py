""" Provides a fast renderer for schema fields. Since this renderer is used
on lists and tables and therefore called many times in a request the following
options were not chosen:

z3c.form display mode rendering - too complicated, hard to customize and slow
zpt templates - quite a bit slower because of features we don't need

The snippets rendered here so simple that string.Template can be used which
is by far the fastest way of doing templates in python.

"""

import string
import zope.component

from zope.schema import (
    Bool,
    Decimal,
    FrozenSet,
    getFields,
    List,
    Set,
    Text,
    Tuple,
    Date,
    Datetime,
    Choice
)
from zope.schema.interfaces import IVocabularyFactory
from plone import api
from plone.namedfile.field import NamedBlobImage, NamedImage
from plone.app.textfield import RichText
from plone.app.uuid.utils import uuidToCatalogBrain
from Products.ZCatalog.interfaces import ICatalogBrain

from seantis.plonetools.schemafields import Email, Website
from seantis.plonetools import tools

from seantis.people import _
from seantis.people.supermodel import (
    get_list_render_options, get_detail_render_options
)
from seantis.people.utils import UUIDList, LinkList


class EmailFieldRenderer(object):

    template = string.Template(u'<a href="mailto:${mail}">${mail}</a>')

    def __call__(self, context, field, options):
        mail = getattr(context, field)
        if mail:
            return self.template.substitute(mail=mail)
        else:
            return u''


class WebsiteFieldRenderer(object):

    template = string.Template(u'<a href="${url}" target="_blank">${url}</a>')

    def __call__(self, context, field, options):
        url = getattr(context, field)
        if url:
            return self.template.substitute(url=url)
        else:
            return u''


class BoolRenderer(object):

    def __call__(self, context, field, options):
        value = getattr(context, field, False)

        if value is True:
            return _(u'Yes')
        else:
            return _(u'No')


class TextRenderer(object):

    def __call__(self, context, field, options):
        return '<br />'.join(getattr(context, field, u'').splitlines())


class DecimalRenderer(object):

    def __call__(self, context, field, options):
        value = getattr(context, field)

        if not value:
            return u''

        # a custom formatter, because the api of Zope's formatter is.. weird?
        formatter = context.REQUEST.locale.numbers.getFormatter('decimal')
        precision = options.by(field).get('precision', 'auto')

        if precision == 'auto':
            formatstring = u'{:,}'
        else:
            formatstring = u'{{:,.{}f}}'.format(precision)

        # this will fail miserably, if the group and the thousand separator
        # should ever be the same, but then again that's stupid
        output = formatstring.format(value)

        output = output.replace('.', 'd')
        output = output.replace(',', 'g')
        output = output.replace('d', formatter.symbols['decimal'])
        output = output.replace('g', formatter.symbols['group'])

        return output


class RichTextRenderer(object):

    def __call__(self, context, field, options):
        return getattr(context, field).output


class ListRenderer(object):

    def __call__(self, context, field, options):
        value = getattr(context, field, tuple())

        if not value:
            return u''

        render_type = options.by(field).get('list_type', 'comma-separated')

        if render_type == 'comma-separated':
            return u', '.join(getattr(context, field, tuple()))
        elif render_type == 'ul':
            return u'<ul class="dense"><li>{}</li></ul>'.format(
                u'</li><li>'.join(
                    value
                )
            )


class LinkListRenderer(object):

    template = string.Template(u'<li><a href="${url}">${title}</a></li>')

    def __call__(self, context, field, options):
        links = getattr(context, field, None)

        if not links:
            return u''

        return u'<ul class="dense">{}</ul>'.format(
            '\n'.join(
                self.template.substitute(url=l[1], title=l[0]) for l in links
            )
        )


class UUIDListRenderer(object):

    template = string.Template(u'<a href="${url}">${title}</a>')

    def __call__(self, context, field, options):
        uuids = getattr(context, field, None)

        if not uuids:
            return u''

        unicode_sortkey = tools.unicode_collate_sortkey()

        brains = (b for b in (uuidToCatalogBrain(uid) for uid in uuids) if b)
        items = sorted(
            ((b.getURL(), b.Title) for b in brains),
            key=lambda i: unicode_sortkey(i[1])
        )

        return ', '.join(
            self.template.substitute(url=url, title=title.decode('utf-8'))
            for url, title in items
        )


class ImageRenderer(object):

    template = string.Template(u'<img src="${url}" />')

    def __call__(self, context, field, options):
        img = getattr(context, field)
        if img:
            if ICatalogBrain.providedBy(context):
                baseurl = context.getURL()
            else:
                baseurl = context.absolute_url()

            size = options.by(field).get('image_size', 'thumb')
            url = '/'.join((baseurl, '@@images', field, size))

            return self.template.substitute(url=url)
        else:
            return u''


class DateRenderer(object):

    def __init__(self, long_format=False, time_only=False):
        self.long_format = long_format
        self.time_only = time_only

    def __call__(self, context, field, options):
        date = getattr(context, field)
        if date:
            return api.portal.get_localized_time(
                datetime=date,
                long_format=self.long_format,
                time_only=self.time_only
            )
        else:
            return u''


class ChoiceRenderer(object):

    def __call__(self, context, field, options):
        value = getattr(context, field)
        schema = tools.get_schema_from_portal_type(context.portal_type)
        name = schema.get(field).vocabularyName
        voc = zope.component.getUtility(IVocabularyFactory, name)(context)

        try:
            return voc.getTerm(value).title
        except LookupError:
            return value


# This is not the best way to match objects to classes, but it sure is the
# fastest. Checking through isinstance would require going through a list.
# Since that can easily happen more than a thousand times in a request it's
# better to be fast than to be right.
renderers = {
    Email: EmailFieldRenderer(),
    Website: WebsiteFieldRenderer(),
    NamedBlobImage: ImageRenderer(),
    NamedImage: ImageRenderer(),
    Text: TextRenderer(),
    RichText: RichTextRenderer(),
    Decimal: DecimalRenderer(),
    Tuple: ListRenderer(),
    List: ListRenderer(),
    Set: ListRenderer(),
    FrozenSet: ListRenderer(),
    list: ListRenderer(),
    set: ListRenderer(),
    tuple: ListRenderer(),
    UUIDList: UUIDListRenderer(),
    LinkList: LinkListRenderer(),
    Bool: BoolRenderer(),
    Datetime: DateRenderer(long_format=True),
    Date: DateRenderer(long_format=False),
    Choice: ChoiceRenderer(),
}


class Options(object):

    def __init__(self, field_options, default_options):
        self.field_options = field_options
        self.default_options = default_options

    def by(self, field):
        if field in self.field_options:
            return self.field_options[field]
        else:
            return self.default_options


class Renderer(object):

    def __init__(self, schema, place, redirects=None):
        assert place in ('list', 'detail')

        self.schema = schema
        self.fields = getFields(schema)
        self.redirects = redirects or {}

        if place == 'list':
            self.options = Options(get_list_render_options(schema), {
                'image_size': 'tile',
                'list_type': 'comma-separated',
                'precision': 'auto'
            })
        else:
            self.options = Options(get_detail_render_options(schema), {
                'image_size': 'mini',
                'list_type': 'comma-separated',
                'precision': 'auto'
            })

    def render(self, context, field):
        field = self.redirects.get(field, field)
        fieldtype = type(self.fields.get(field, getattr(context, field, None)))

        if fieldtype in renderers:
            return renderers[fieldtype](context, field, self.options)
        else:
            return getattr(context, field)
