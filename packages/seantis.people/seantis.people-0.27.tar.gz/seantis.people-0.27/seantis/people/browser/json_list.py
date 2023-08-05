import json
from collections import namedtuple

from five import grok

from seantis.people.interfaces import IList
from seantis.people.browser import BaseView


JsonField = namedtuple('JsonField', ['scope', 'getter'])


class JsonListView(BaseView):

    permission = 'zope2.View'
    grok.require(permission)
    grok.context(IList)
    grok.name('json')

    available_fields = {
        'uuid': lambda b: b.UID,
        'title': lambda b: b.Title,
        'url': lambda b: b.getURL()
    }

    def render(self):
        fields = self.available_fields.items()

        records = []

        for brain in self.context.people():
            records.append(dict((field, fn(brain)) for field, fn in fields))

        self.request.response.setHeader('Content-type', 'application/json')
        return json.dumps(records)
