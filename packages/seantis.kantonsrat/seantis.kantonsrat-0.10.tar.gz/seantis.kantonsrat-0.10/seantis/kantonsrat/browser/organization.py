from collections import namedtuple
from five import grok

from plone.folder.interfaces import IExplicitOrdering
from plone.uuid.interfaces import IUUID
from zope.component import queryUtility

from seantis.kantonsrat.browser.base import BaseView
from seantis.kantonsrat.interfaces import IMotionsProvider
from seantis.kantonsrat.reports import get_available_reports
from seantis.kantonsrat.types import IOrganization


class OrganizationView(BaseView):

    grok.require('zope2.View')
    grok.context(IOrganization)
    grok.name('view')

    template = grok.PageTemplateFile('templates/organization.pt')

    def present_members(self):
        return self.context.memberships('present')

    def past_members(self):
        return self.context.memberships('past')

    def future_members(self):
        return self.context.memberships('future')

    def show_report(self):
        # yep, this is supposed to be hardcoded:
        # https://github.com/seantis/seantis.kantonsrat/issues/11
        return self.context.aq_parent.id == 'kommissionen'

    def submitted_motions(self):
        motions_provider = queryUtility(IMotionsProvider)
        if motions_provider:
            return motions_provider.motions_by_entity(IUUID(self.context))
        else:
            return []

    def reports(self):
        Report = namedtuple("Report", ['url', 'title', 'description'])
        baseurl = self.context.absolute_url()
        reports = []

        for id, report in get_available_reports().items():
            reports.append(
                Report(
                    (
                        '{}/kantonsrat-report?id={}'
                        '&with-this-organization={}'
                        '&without-table-of-content'
                    ).format(baseurl, id, self.context.UID()),
                    report['title'],
                    report['description']
                )
            )

        return reports


class OrganizationMembershipReorderView(BaseView):

    grok.require('cmf.ModifyPortalContent')
    grok.context(IOrganization)
    grok.name('reorder-memberships')

    def update(self):
        self.reorder_memberships()

    def reorder_memberships(self):
        order = self.request.get('order')

        if not order:
            return

        IExplicitOrdering(self.context).moveObjectsToTop(order.split(','))

    def render(self):
        return u''
