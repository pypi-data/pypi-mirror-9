import codecs

from copy import copy
from five import grok
from importlib import import_module
from plone import api
from plone.directives import form
from z3c.form import field
from z3c.form.interfaces import HIDDEN_MODE
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form.browser.radio import RadioFieldWidget
from zope import schema
from zope.component import getAdapters
from zope.i18nmessageid import MessageFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from seantis.people import _
from seantis.people import catalog_id
from seantis.people.interfaces import IList, IExportVariant
from seantis.people.browser import BaseForm
from seantis.people.errors import ContentExportError
from seantis.people.content.export_content import (
    supported_formats, export_people
)

uppercase_formats = [f.upper() for f in supported_formats]


class IExportFormSchema(form.Schema):

    export_fields = schema.List(
        title=_(u"Fields"),
        description=_(u"Fields to include in the export"),
        required=True,
        value_type=schema.Choice(values=[]),
    )

    export_format = schema.Choice(
        title=_(u"Format"),
        values=uppercase_formats,
        default='CSV'
    )

    variant = schema.Choice(
        title=_(u"Variant"),
        values=[]
    )

    review_state = schema.Choice(
        title=_(u"State"),
        values=[]
    )

    include_inactive = schema.Bool(
        title=_(u"Include Inactive"),
        default=True
    )


class ExportForm(BaseForm):

    grok.require('cmf.ModifyPortalContent')
    grok.context(IList)
    grok.name('export')

    ignoreContext = True
    output = None
    enable_unload_protection = False

    def render(self):
        if self.output:
            return self.output
        else:
            return super(ExportForm, self).render()

    @property
    def label(self):
        return _(u"Export ${name}", mapping={
            'name': self.context.title
        })

    @property
    def portal_type(self):
        return self.context.used_type()

    @property
    def portal_type_fields(self):
        result = []

        if self.portal_type:
            schema = self.portal_type.lookupSchema()

            for id, f in field.Fields(schema).items():
                result.append((id, f.field.title))

            module = '.'.join(self.portal_type.klass.split('.')[:-1])
            klass = self.portal_type.klass.split('.')[-1]
            klass = getattr(import_module(module), klass)

            membership_fields = klass().membership_fields
            for id in sorted(membership_fields):
                result.append((id, membership_fields[id]))

        return result

    @property
    def fields(self):
        fields = field.Fields(IExportFormSchema)
        self.prepare_export_fields(fields)
        self.prepare_format_field(fields)
        self.prepare_review_states_field(fields)
        self.prepare_variants(fields)
        return fields

    @property
    def hide_include_inactive(self):
        """ The include inactive flag is only shown if any people have it
        set. If it wouldn't make a difference, don't include it.

        """
        path = {
            'query': '/'.join(self.context.getPhysicalPath()), 'depth': 1
        }
        catalog = api.portal.get_tool(catalog_id)
        return len(catalog(path=path, is_active_person=False)) == 0

    def updateWidgets(self):
        super(ExportForm, self).updateWidgets()

        if self.hide_include_inactive:
            self.widgets['include_inactive'].mode = HIDDEN_MODE

        if len(self.available_variants) == 1:
            self.widgets['variant'].mode = HIDDEN_MODE

    def prepare_export_fields(self, fields):

        vocabulary = SimpleVocabulary(terms=[
            SimpleTerm(id, title=title)
            for id, title in self.portal_type_fields
        ])

        default_values = [i[0] for i in self.portal_type_fields]

        f = fields['export_fields']
        f.field = copy(f.field)

        f.field.value_type.vocabulary = vocabulary
        f.field.default = default_values

        f.widgetFactory = CheckBoxFieldWidget

    def prepare_format_field(self, fields):
        f = fields['export_format']
        f.field = copy(f.field)
        f.widgetFactory = RadioFieldWidget

    def prepare_review_states_field(self, fields):

        vocabulary = SimpleVocabulary(terms=[
            SimpleTerm(id, title=title)
            for id, title in self.available_review_states
        ])

        f = fields['review_state']
        f.field = copy(f.field)

        f.field.vocabulary = vocabulary
        f.field.default = '__all__'

        f.widgetFactory = RadioFieldWidget

    def prepare_variants(self, fields):

        vocabulary = SimpleVocabulary(terms=[
            SimpleTerm(name, title=self.translate(title))
            for name, title in self.available_variants
        ])

        f = fields['variant']
        f.field = copy(f.field)

        f.field.vocabulary = vocabulary
        f.field.default = '__none__'

        f.widgetFactory = RadioFieldWidget

    @property
    def available_review_states(self):
        all_states = [
            ('__all__', _(u'All'))
        ]

        used_type = self.context.used_type()
        if not used_type:
            return all_states

        actual_states = set(b.review_state for b in self.context.people())
        wftool = api.portal.get_tool('portal_workflow')

        _plone = MessageFactory('plone')

        for state in actual_states:
            all_states.append((
                state, _plone(
                    wftool.getTitleForStateOnType(state, used_type.id)
                )
            ))

        return all_states

    @property
    def available_variants(self):
        exports = [
            ('__none__', _(u'Standard'))
        ]

        for name, export in getAdapters((self.context, ), IExportVariant):
            if export.can_handle_type(self.portal_type):
                exports.append((name, export.title))

        return exports

    def get_variant_by_name(self, name):
        if name == '__none__':
            return None

        for variant, export in getAdapters((self.context, ), IExportVariant):
            if variant == name and export.can_handle_type(self.portal_type):
                return export

        return None

    @property
    def available_actions(self):
        yield dict(name='export', title=_(u"Export"),
                   css_class='context allowMultiSubmit')
        yield dict(name='cancel', title=_(u"Cancel"))

    def handle_export(self):
        try:
            export_fields = self.parameters.get('export_fields')
            export_fields = [
                (id, title) for id, title
                in self.portal_type_fields
                if id in export_fields
            ]

            review_state = self.parameters.get('review_state')
            review_state = None if review_state == '__all__' else review_state

            include_inactive = self.parameters.get('include_inactive')

            dataset = export_people(
                self.request,
                self.context,
                self.portal_type.id,
                export_fields,
                review_state,
                include_inactive
            )

            variant = self.get_variant_by_name(self.parameters.get('variant'))
            if variant:
                dataset = variant.adjust_dataset(dataset, self.parameters)

                if dataset is None:
                    raise ContentExportError(
                        _(u"The selected variant could not be applied")
                    )

            format = self.parameters.get('export_format').lower()
            filename = '%s.%s' % (self.context.title, format)
            filename = codecs.utf_8_encode('filename="%s"' % filename)[0]

            output = getattr(dataset, format)

            RESPONSE = self.request.RESPONSE
            RESPONSE.setHeader("Content-disposition", filename)
            RESPONSE.setHeader(
                "Content-Type", "application/%s;charset=utf-8" % format
            )
            RESPONSE.setHeader("Content-Length", len(output))

            self.output = output

        except ContentExportError as e:
            self.raise_action_error(e.translate(self.request))
