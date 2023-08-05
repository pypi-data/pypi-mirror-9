import json
from collections import namedtuple

from five import grok

from plone import api

from seantis.people.interfaces import IList
from seantis.kantonsrat.browser.base import BaseView


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

    def records(self):
        people = self.context.people(
            include_inactive=True, unrestricted_search=True
        )
        for brain in people:
            yield 'person', brain

        for org_type in ('committee', 'party', 'faction'):
            brains = self.organizations_by_type(
                org_type, unrestricted_search=True
            )

            for brain in brains:
                yield org_type, brain

    def organizations_by_type(self, org_type, unrestricted_search=False):
        catalog = api.portal.get_tool('portal_catalog')

        if unrestricted_search:
            search = catalog.unrestrictedSearchResults
        else:
            search = catalog

        return search(organization_type=org_type)

    def render(self):
        fields = self.available_fields.items()

        records = []

        for type, brain in self.records():
            record = dict((field, fn(brain)) for field, fn in fields)
            record['type'] = type

            records.append(record)

        self.request.response.setHeader('Content-type', 'application/json')
        return json.dumps(records)
