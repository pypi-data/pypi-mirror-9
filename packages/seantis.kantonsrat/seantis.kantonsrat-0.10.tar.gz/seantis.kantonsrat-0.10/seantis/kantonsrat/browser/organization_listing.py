from collections import namedtuple
from plone import api

from five import grok
from zope.security import checkPermission

from Products.ATContentTypes.interface import IATFolder

from seantis.kantonsrat.reports import get_available_reports
from seantis.kantonsrat.types.organization import is_organization_visible
from seantis.kantonsrat.browser.base import BaseView


class Listing(BaseView):

    grok.context(IATFolder)
    grok.require('zope2.View')

    grok.name('organization_listing')

    template = grok.PageTemplateFile('templates/organization_listing.pt')

    def organizations(self):
        catalog = api.portal.get_tool('portal_catalog')
        path = '/'.join(self.context.getPhysicalPath())

        organizations = catalog.searchResults({
            'path': {'query': path, 'depth': 1},
            'portal_type': 'seantis.kantonsrat.organization'
        })

        def case_sensitive_sort_without_state(item):
            return item.Title

        # moves the inactive organizations at the end of the list
        def case_sensitive_sort_with_state(item):
            if self.is_active(item):
                return item.Title

            return ''.join(('zzz', item.Title))

        # only managers need the stateful sorting, other users get the faster
        # sort instead. It would be better to use a sort index here, but this
        # may not be final and it should be fast enough anyway.
        if self.is_manager():
            return sorted(organizations, key=case_sensitive_sort_with_state)
        else:
            return sorted(organizations, key=case_sensitive_sort_without_state)

    def is_manager(self):
        return checkPermission('cmf.ModifyPortalContent', self.context)

    def is_visible(self, organization):
        if self.is_manager():
            return True

        return self.is_active(organization)

    def show_reports(self):
        # yep, this is supposed to be hardcoded:
        # https://github.com/seantis/seantis.kantonsrat/issues/11
        return self.context.id == 'kommissionen'

    def is_active(self, organization):
        return is_organization_visible(organization)

    def reports(self):
        Report = namedtuple("Report", ['url', 'title', 'description'])
        baseurl = self.context.absolute_url()

        reports = []
        for id, report in get_available_reports().items():
            reports.append(
                Report(
                    '{}/kantonsrat-report?id={}'.format(baseurl, id),
                    report['title'],
                    report['description']
                )
            )

        return reports
