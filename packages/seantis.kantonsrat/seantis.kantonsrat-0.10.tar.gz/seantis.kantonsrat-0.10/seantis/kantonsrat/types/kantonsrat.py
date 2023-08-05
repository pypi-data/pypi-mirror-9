import logging
log = logging.getLogger('seantis.kantonsrat')

from datetime import date
from five import grok
from zope.interface import Interface, invariant, Invalid
from zope.component import queryUtility

from plone import api
from plone.directives import form
from plone.uuid.interfaces import IUUID

from seantis.people.interfaces import ICompoundColumns
from seantis.people.types.base import PersonBase
from seantis.people.interfaces import IPerson
from seantis.people.utils import LinkList

from seantis.kantonsrat import _
from seantis.kantonsrat.interfaces import IMotionsProvider


class IMember(form.Schema):
    form.model("kantonsrat.xml")

    @invariant
    def has_valid_daterange(Member):
        if Member.start is None:
            return

        if Member.end is None:
            return

        if Member.start > Member.end:
            raise Invalid(_(u"The end cannt be before the start"))


class Member(PersonBase):

    custom_titles = {
        'motions': _(u'Submitted Motions')
    }

    def exclude_from_nav(self):
        return not self.is_active_person

    @property
    def is_active_person(self):
        today = date.today()
        start, end = (self.start or date.min), (self.end or date.max)

        return (start <= today and today <= end)

    @property
    def membership_fields(self):
        parent_fields = super(Member, self).membership_fields
        parent_fields.update({
            'party_memberships': _(u'Party'),
            'faction_memberships': _(u'Factions'),
            'committee_memberships': _(u'Committees')
        })

        return parent_fields

    def get_organizations_filter(self, orgtype, active_only=True):
        catalog = api.portal.get_tool('portal_catalog')
        organizations = set(b.UID for b in catalog(organization_type=orgtype))

        org_filter = lambda uuid, memberships: (
            uuid in organizations and self.select_active_memberships(
                memberships
            )
        )

        return org_filter

    def organization_uuids_by_type(self, orgtype, active_only=True):
        return IPerson(self).organization_uuids(
            org_filter=self.get_organizations_filter(orgtype, active_only)
        )

    def organizations_by_type(self, orgtype, active_only=True):
        return IPerson(self).organizations(
            org_filter=self.get_organizations_filter(orgtype, active_only)
        )

    def memberships_by_type(self, orgtype, active_only=True):
        result = IPerson(self).memberships(
            org_filter=self.get_organizations_filter(orgtype)
        )

        if active_only:
            return self.select_active_organizations(result)
        else:
            return result

    def select_active_organizations(self, organizations):
        result = {}
        for organization, memberships in organizations.items():
            memberships = self.select_active_memberships(memberships)

            if not memberships:
                continue

            result[organization] = memberships

        return result

    def select_active_memberships(self, memberships):
        today = date.today()
        active = filter(
            lambda m: (
                (m.start or date.min) <= today and today <= (m.end or date.max)
            ), memberships
        )

        return sorted(active, key=lambda m: (
            m.start or date.min, m.end or date.max
        ))

    @property
    def parties(self):
        return self.organizations_by_type('party')

    @property
    def party_uuids(self):
        return self.organization_uuids_by_type('party')

    @property
    def party_memberships(self):
        return self.memberships_by_type('party')

    @property
    def committees(self):
        return self.organizations_by_type('committee')

    @property
    def committee_uuids(self):
        return self.organization_uuids_by_type('committee')

    @property
    def committee_memberships(self):
        return self.memberships_by_type('committee')

    @property
    def factions(self):
        return self.organizations_by_type('faction')

    @property
    def faction_uuids(self):
        return self.organization_uuids_by_type('faction')

    @property
    def faction_memberships(self):
        return self.memberships_by_type('faction')

    @property
    def motions(self):
        try:
            motions_provider = queryUtility(IMotionsProvider)

            if motions_provider:
                motions = motions_provider.motions_by_entity(IUUID(self))
                return LinkList((m.title, m.url) for m in motions)
        except:
            log.exception('could not retrieve motions')

        return []


class CompoundColumns(grok.Adapter):

    grok.name('kantonsrat-compound-columns')
    grok.provides(ICompoundColumns)
    grok.context(Interface)

    def get_compound_columns(self):
        return {
            'parties': 'party_uuids',
            'committees': 'committee_uuids',
            'factions': 'faction_uuids'
        }
