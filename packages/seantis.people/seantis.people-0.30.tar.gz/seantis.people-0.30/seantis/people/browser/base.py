from five import grok

from seantis.plonetools.browser import BaseView as SharedBaseView
from seantis.plonetools.browser import BaseForm as SharedBaseForm

from seantis.people.interfaces import ISeantisPeopleSpecific


class BaseView(SharedBaseView):

    grok.baseclass()
    grok.layer(ISeantisPeopleSpecific)

    domain = 'seantis.people'


class BaseForm(SharedBaseForm):

    grok.baseclass()
    grok.layer(ISeantisPeopleSpecific)

    domain = 'seantis.people'
